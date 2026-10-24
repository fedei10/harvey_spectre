import unittest
from unittest.mock import AsyncMock, patch
import httpx
from app.main import app


class InfrastructureConnectionsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.old_engine = getattr(app.state, "postgres_engine", None)
        self.old_redis = getattr(app.state, "redis", None)
        app.state.postgres_engine = object()
        app.state.redis = object()
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self):
        app.state.postgres_engine = self.old_engine
        app.state.redis = self.old_redis
        await self.client.aclose()

    async def test_healthy(self):
        with patch("app.main.check_postgres", new_callable=AsyncMock, return_value=True), \
             patch("app.main.check_redis", new_callable=AsyncMock, return_value=True):
            response = await self.client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"postgres": "connected", "redis": "connected"}
        )

    async def test_failed_redis(self):
        with patch("app.main.check_postgres", new_callable=AsyncMock, return_value=True), \
             patch("app.main.check_redis", new_callable=AsyncMock, side_effect=OSError("secret")):
            response = await self.client.get("/test")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["postgres"], "connected")
        self.assertEqual(response.json()["redis"], "disconnected")
        self.assertNotIn("secret", response.text)
