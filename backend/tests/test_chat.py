import unittest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from groq import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from pydantic import SecretStr

from app.ai_engineering.agent.graph import build_graph
from app.config import settings
from app.main import app


class ChatTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        app.state.graph = build_graph(InMemorySaver())
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
        self.model_patch = patch("app.ai_engineering.agent.nodes.llm.ChatGroq")
        self.model = self.model_patch.start()
        self.bound = AsyncMock()
        self.model.return_value.bind_tools.return_value = self.bound
        self.key_patch = patch.object(settings, "GROQ_API_KEY", SecretStr("test-key"))
        self.key_patch.start()

    async def asyncTearDown(self):
        self.key_patch.stop()
        self.model_patch.stop()
        await self.client.aclose()

    async def test_history_and_conversation_isolation(self):
        self.bound.ainvoke.return_value = AIMessage(content="Hello!")
        first = await self.client.post("/v1/chat", json={"message": "Hello"})
        self.assertEqual(first.status_code, 200)
        cid = first.json()["conversation_id"]
        self.assertTrue(cid)
        self.assertEqual(first.json()["response"], "Hello!")
        second = await self.client.post("/v1/chat", json={"message": "Again", "conversation_id": cid})
        self.assertEqual(second.json()["conversation_id"], cid)
        self.assertEqual([m.content for m in self.bound.ainvoke.call_args.args[0][1:]], ["Hello", "Hello!", "Again"])
        third = await self.client.post("/v1/chat", json={"message": "New chat"})
        self.assertNotEqual(third.json()["conversation_id"], cid)
        self.assertEqual(len(self.bound.ainvoke.call_args.args[0]), 2)
        self.assertNotIn("base_url", self.model.call_args.kwargs)
        self.assertEqual(self.model.call_args.kwargs["model"], settings.GROQ_MODEL_NAME)
        self.assertEqual(self.model.call_args.kwargs["api_key"], "test-key")

    async def test_tool_result_returns_to_model(self):
        self.bound.ainvoke.side_effect = [
            AIMessage(content="", tool_calls=[{"name": "get_current_time", "args": {}, "id": "clock-call"}]),
            AIMessage(content="The current time is available."),
        ]
        response = await self.client.post("/v1/chat", json={"message": "What time is it?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.bound.ainvoke.await_count, 2)
        self.assertEqual(self.bound.ainvoke.call_args.args[0][-1].type, "tool")

    async def test_blank_messages(self):
        for message in ["", "   "]:
            response = await self.client.post("/v1/chat", json={"message": message})
            self.assertEqual(response.status_code, 422)
        self.bound.ainvoke.assert_not_awaited()

    async def test_provider_errors(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        for error, status in [(APIConnectionError(request=request), 502), (APITimeoutError(request=request), 504)]:
            self.bound.ainvoke.side_effect = error
            response = await self.client.post("/v1/chat", json={"message": "Hi"})
            self.assertEqual(response.status_code, status)

    async def test_missing_key(self):
        with patch.object(settings, "GROQ_API_KEY", None):
            response = await self.client.post("/v1/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 503)

    async def test_empty_reply(self):
        self.bound.ainvoke.return_value = AIMessage(content="")
        response = await self.client.post("/v1/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 503)

    async def test_authentication_and_quota_failures(self):
        for error_class, status, detail in [(AuthenticationError, 401, "API key"), (RateLimitError, 429, "quota")]:
            response = httpx.Response(status, request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"))
            self.bound.ainvoke.side_effect = error_class("Provider failure", response=response, body=None)
            result = await self.client.post("/v1/chat", json={"message": "Hi"})
            self.assertEqual(result.status_code, 503)
            self.assertIn(detail, result.json()["detail"])

    async def test_chat_does_not_require_codecraft_key(self):
        self.bound.ainvoke.return_value = AIMessage(content="Hello from Groq!")
        with patch.object(settings, "OPENAI_API_KEY", None):
            response = await self.client.post("/v1/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Hello from Groq!")

    async def test_history_persists_with_same_checkpointer(self):
        # Unit-level thread persistence; cloud Postgres is an integration test.
        self.bound.ainvoke.return_value = AIMessage(content="Remembered.")
        response = await self.client.post(
            "/v1/chat", json={"message": "Remember orange", "conversation_id": "persist-1"}
        )
        self.assertEqual(response.status_code, 200)
        response = await self.client.post(
            "/v1/chat", json={"message": "What word?", "conversation_id": "persist-1"}
        )
        self.assertEqual(response.status_code, 200)
        messages = self.bound.ainvoke.call_args.args[0]
        self.assertEqual(
            [m.content for m in messages[1:]],
            ["Remember orange", "Remembered.", "What word?"],
        )

    async def test_health_checks_provider_and_reports_errors(self):
        with patch("app.api.v1.health.get_models", return_value=[{"id": "test-model"}]) as models:
            result = await self.client.get("/v1/health/CODE_CRAFT")
            self.assertEqual(result.status_code, 200)
            models.assert_called_once()
            result = await self.client.get("/v1/health/CODE_CRAFT/GET_MODELS")
            self.assertEqual(result.json()["models"], [{"id": "test-model"}])
        with patch("app.api.v1.health.get_models", side_effect=ValueError("Missing key")):
            result = await self.client.get("/v1/health/CODE_CRAFT/GET_MODELS")
            self.assertEqual(result.status_code, 503)
