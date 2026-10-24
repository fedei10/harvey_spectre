"""Cloud PostgreSQL checkpoint persistence for LangGraph.

This is not a semantic memory store; it persists/retrieves graph state by thread_id.
Keep the pool open for the FastAPI application's lifespan.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.engine import URL, make_url

from app.config import settings


def get_checkpoint_dsn() -> str:
    """Get a Psycopg-compatible URL from a dedicated or shared database config."""
    configured = settings.LANGGRAPH_DATABASE_URL or settings.DATABASE_URL
    if configured:
        url = make_url(configured.get_secret_value())
        if url.drivername not in {
            "postgresql", "postgres", "postgresql+psycopg2",
            "postgresql+psycopg", "postgresql+asyncpg",
        }:
            raise ValueError("A PostgreSQL connection URL is required.")
        # Psycopg does not understand SQLAlchemy's +driver URL schemes.
        return url.set(drivername="postgresql").render_as_string(
            hide_password=False
        )

    if not settings.POSTGRES_PASSWORD:
        raise ValueError(
            "Configure LANGGRAPH_DATABASE_URL, DATABASE_URL, "
            "or POSTGRES_HOST/USER/PASSWORD/DB in backend/.env."
        )

    # URL.create correctly encodes passwords containing special characters.
    url = URL.create(
        drivername="postgresql",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        query={"sslmode": settings.POSTGRES_SSLMODE},
    )
    return url.render_as_string(hide_password=False)


@asynccontextmanager
async def postgres_checkpointer(*, setup: bool = False) -> AsyncIterator[AsyncPostgresSaver]:
    """Start a managed connection pool; optionally initialize LangGraph tables.

    setup=True is intended for the one-time init script, not normal server start.
    """
    async with AsyncConnectionPool(
        conninfo=get_checkpoint_dsn(),
        min_size=settings.LANGGRAPH_POOL_MIN_SIZE,
        max_size=settings.LANGGRAPH_POOL_MAX_SIZE,
        max_idle=300,
        max_lifetime=1800,
        timeout=10,
        open=False,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row,
            "prepare_threshold": 0,
        },
    ) as pool:
        # Fail fast on missing credentials, unreachable cloud DB, or SSL problems.
        await pool.wait(timeout=20)
        checkpointer = AsyncPostgresSaver(pool)
        if setup:
            await checkpointer.setup()
        yield checkpointer
