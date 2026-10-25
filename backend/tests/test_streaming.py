import asyncio
import json
import unittest
from unittest.mock import patch

import httpx
from groq import RateLimitError
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import SecretStr

from app.ai_engineering.agent.graph import build_graph
from app.config import settings
from app.main import app
from app.services.chat import stream_chat


def events(body):
    return [json.loads(line[6:]) for line in body.splitlines()
            if line.startswith('data: ')]


class StreamingTests(unittest.IsolatedAsyncioTestCase):
    async def test_streams_individual_chunks_and_saves_history(self):
        graph = build_graph(InMemorySaver())
        text = 'Hello\n"world" 🌍'
        with patch.object(settings, 'GROQ_API_KEY', SecretStr('test-key')):
            with patch('app.ai_engineering.agent.nodes.llm.ChatGroq') as factory:
                factory.return_value.bind_tools.return_value = FakeListChatModel(responses=[text])
                frames = [frame async for frame in stream_chat(graph, 'Hi', 'stream-test')]
        chunks = events(''.join(frames))
        deltas = [chunk['text'] for chunk in chunks if chunk['type'] == 'delta']
        self.assertGreater(len(deltas), 1)
        self.assertEqual(''.join(deltas), text)
        self.assertEqual(chunks[-1]['type'], 'done')
        self.assertEqual(chunks[0]['conversation_id'], 'stream-test')
        self.assertFalse(any(chunk['type'] == 'error' for chunk in chunks))
        state = await graph.aget_state({'configurable': {'thread_id': 'stream-test'}})
        self.assertEqual([message.content for message in state.values['messages']], ['Hi', text])

    async def test_error_after_partial_reply_is_safe_and_terminal(self):
        class Graph:
            async def astream(self, *args, **kwargs):
                yield AIMessageChunk(content='Hello'), {'langgraph_node': 'llm'}
                response = httpx.Response(429, request=httpx.Request('POST', 'https://api.groq.com'))
                raise RateLimitError('private details', response=response, body=None)
        chunks = events(''.join([frame async for frame in stream_chat(Graph(), 'Hi', None)]))
        error = next(chunk for chunk in chunks if chunk['type'] == 'error')
        self.assertIn('quota', error['message'])
        self.assertNotIn('private', error['message'])
        self.assertEqual(chunks[-1]['type'], 'done')

    async def test_cancellation_is_not_converted_to_an_error_reply(self):
        class Graph:
            async def astream(self, *args, **kwargs):
                yield AIMessageChunk(content='Hello'), {'langgraph_node': 'llm'}
                raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            _ = [frame async for frame in stream_chat(Graph(), 'Hi', None)]

    async def test_stream_endpoint_headers_validation_and_missing_key(self):
        app.state.graph = build_graph(InMemorySaver())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            with patch.object(settings, 'GROQ_API_KEY', None):
                response = await client.post('/v1/chat/stream', json={'message': 'Hi'})
                self.assertEqual(response.status_code, 503)
            response = await client.post('/v1/chat/stream', json={'message': '   '})
            self.assertEqual(response.status_code, 422)
            with patch.object(settings, 'GROQ_API_KEY', SecretStr('test-key')):
                with patch('app.ai_engineering.agent.nodes.llm.ChatGroq') as factory:
                    factory.return_value.bind_tools.return_value = FakeListChatModel(responses=['OK'])
                    response = await client.post('/v1/chat/stream', json={'message': 'Hi'})
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('x-vercel-ai-ui-message-stream', response.headers)
            self.assertIn('text/event-stream', response.headers['content-type'])
            self.assertTrue(any(chunk['type'] == 'delta' for chunk in events(response.text)))
