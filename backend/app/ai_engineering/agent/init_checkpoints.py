"""Initialize LangGraph-managed PostgreSQL checkpoint tables once.

Usage from backend/: python -m app.ai_engineering.agent.init_checkpoints
This is separate from Alembic migrations for your application's ORM tables.
"""
import asyncio

from app.ai_engineering.agent.checkpoint import postgres_checkpointer


async def main() -> None:
    async with postgres_checkpointer(setup=True):
        print("LangGraph PostgreSQL checkpoint tables initialized.")


if __name__ == "__main__":
    asyncio.run(main())
