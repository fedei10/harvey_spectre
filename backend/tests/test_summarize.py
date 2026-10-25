import unittest
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from pydantic import SecretStr

from app.ai_engineering.agent.nodes.summarize import summarize_conversation
from app.config import settings


def conversation(turns: int):
    messages = []
    for i in range(turns):
        messages += [HumanMessage(f"q{i}", id=f"h{i}"), AIMessage(f"a{i}", id=f"a{i}")]
    return {"messages": messages}


def reply(text: str, finish_reason: str):
    return AIMessage(text, response_metadata={"finish_reason": finish_reason})


class SummarizeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_patch = patch.object(settings, "GROQ_API_KEY", SecretStr("test-key"))
        self.key_patch.start()
        self.model_patch = patch("app.ai_engineering.agent.nodes.summarize.ChatGroq")
        self.model = self.model_patch.start().return_value
        self.model.ainvoke = AsyncMock()

    async def asyncTearDown(self):
        self.model_patch.stop()
        self.key_patch.stop()

    async def test_short_conversation_is_not_summarized(self):
        self.assertEqual(await summarize_conversation(conversation(11)), {})
        self.model.ainvoke.assert_not_called()

    async def test_success_removes_all_but_last_four_user_turns(self):
        self.model.ainvoke.return_value = reply("User needs EUR rounding.", "stop")
        result = await summarize_conversation(conversation(12))
        self.assertEqual(result["summary"], "User needs EUR rounding.")
        removed = [m.id for m in result["messages"]]
        self.assertTrue(all(isinstance(m, RemoveMessage) for m in result["messages"]))
        self.assertEqual(removed, [f"{p}{i}" for i in range(8) for p in "ha"])

    async def test_truncated_summary_keeps_history(self):
        self.model.ainvoke.return_value = reply("User needs EUR rou", "length")
        self.assertEqual(await summarize_conversation(conversation(12)), {})

    async def test_empty_summary_keeps_history(self):
        self.model.ainvoke.return_value = reply("  ", "stop")
        self.assertEqual(await summarize_conversation(conversation(12)), {})

    async def test_summarizer_error_keeps_history(self):
        self.model.ainvoke.side_effect = TimeoutError()
        self.assertEqual(await summarize_conversation(conversation(12)), {})


if __name__ == "__main__":
    unittest.main()
