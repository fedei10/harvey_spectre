"""Opt-in cloud Postgres persistence test.

Run: RUN_POSTGRES_INTEGRATION=1 python -m unittest tests/test_postgres_checkpoint_integration.py
Requires checkpoint tables initialized and a configured cloud Postgres connection.
"""
import os
import unittest
from uuid import uuid4

from langgraph.graph import MessagesState, START, StateGraph
from app.ai_engineering.agent.checkpoint import postgres_checkpointer


@unittest.skipUnless(
    os.getenv("RUN_POSTGRES_INTEGRATION") == "1",
    "Set RUN_POSTGRES_INTEGRATION=1 to test the real PostgreSQL connection",
)
class PostgresPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_same_thread_survives_new_connection_pool(self):
        thread_id = "integration-" + str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        def node(state: MessagesState):
            return {"messages": [{"role": "assistant", "content": "ack"}]}

        builder = StateGraph(MessagesState)
        builder.add_node("test", node)
        builder.add_edge(START, "test")

        async with postgres_checkpointer() as saver:
            graph = builder.compile(checkpointer=saver)
            await graph.ainvoke(
                {"messages": [{"role": "user", "content": "Remember me"}]},
                config,
            )

        # A newly opened database pool can still retrieve persisted state.
        async with postgres_checkpointer() as saver:
            graph = builder.compile(checkpointer=saver)
            state = await graph.aget_state(config)
            self.assertEqual(
                state.values["messages"][0].content,
                "Remember me",
            )
