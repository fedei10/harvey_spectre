import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from groq import Groq
from pydantic import SecretStr

from app.config import settings
from app.main import app


class GroqConnectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(settings, "CHECKPOINT_DB", str(Path(self.directory.name) / "test.sqlite"))
        self.db_patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.db_patch.stop()
        self.directory.cleanup()

    def transport_client(self, handler, **kwargs):
        return Groq(http_client=httpx.Client(transport=httpx.MockTransport(handler)), **kwargs)

    def test_real_sdk_sends_unwrapped_key_and_correct_model(self):
        def handler(request):
            self.assertEqual(request.headers["authorization"], "Bearer test-groq-key")
            self.assertEqual(json.loads(request.content)["model"], "openai/gpt-oss-120b")
            return httpx.Response(200, json={
                "id": "test", "object": "chat.completion", "created": 1,
                "model": "openai/gpt-oss-120b",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}, "finish_reason": "stop"}],
            })
        with patch.object(settings, "GROQ_API_KEY", SecretStr("test-groq-key")), patch.object(settings, "GROQ_MODEL_NAME", "openai/gpt-oss-120b"):
            with patch("app.services.groq.connection.Groq", side_effect=lambda **kwargs: self.transport_client(handler, **kwargs)):
                for route, key in [("/test", "groq_chat"), ("/v1/health/GROQ", "status")]:
                    response = self.client.get(route)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()[key], "Groq connection successful")

    def test_provider_failures(self):
        for upstream, expected in [(401, 503), (429, 503), (500, 502)]:
            with self.subTest(upstream=upstream):
                def handler(request):
                    return httpx.Response(upstream, json={"error": {"message": "private provider detail"}})
                with patch.object(settings, "GROQ_API_KEY", SecretStr("test-key")):
                    with patch("app.services.groq.connection.Groq", side_effect=lambda **kwargs: self.transport_client(handler, **kwargs)):
                        response = self.client.get("/test")
                        self.assertEqual(response.status_code, expected)
                        self.assertNotIn("private provider detail", response.text)

    def test_timeout(self):
        def handler(request):
            raise httpx.ReadTimeout("timeout", request=request)
        with patch.object(settings, "GROQ_API_KEY", SecretStr("test-key")):
            with patch("app.services.groq.connection.Groq", side_effect=lambda **kwargs: self.transport_client(handler, **kwargs)):
                self.assertEqual(self.client.get("/test").status_code, 504)

    def test_missing_key(self):
        for key in [None, SecretStr(""), SecretStr("   ")]:
            with patch.object(settings, "GROQ_API_KEY", key):
                with patch("app.services.groq.connection.Groq") as factory:
                    self.assertEqual(self.client.get("/test").status_code, 503)
                    factory.assert_not_called()
