import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI

from app.main import lifespan


class LifespanTests(unittest.IsolatedAsyncioTestCase):
    async def test_initializes_checkpoints_before_building_graph(self):
        application = FastAPI()
        context = MagicMock()
        context.__aenter__ = AsyncMock()
        context.__aexit__ = AsyncMock(return_value=False)
        saver = context.__aenter__.return_value
        with patch('app.main.postgres_checkpointer', return_value=context) as factory, \
             patch('app.main.build_graph') as build:
            async with lifespan(application):
                factory.assert_called_once_with(setup=True)
                context.__aenter__.assert_awaited_once()
                build.assert_called_once_with(saver)
                self.assertIs(application.state.graph, build.return_value)
            context.__aexit__.assert_awaited_once()

    async def test_initialization_failure_prevents_serving_requests(self):
        application = FastAPI()
        context = MagicMock()
        context.__aenter__ = AsyncMock(side_effect=RuntimeError('setup failed'))
        with patch('app.main.postgres_checkpointer', return_value=context), \
             patch('app.main.build_graph') as build:
            with self.assertRaisesRegex(RuntimeError, 'setup failed'):
                async with lifespan(application):
                    self.fail('Application started without checkpoint tables')
            build.assert_not_called()
