"""Async PostgreSQL and Redis connectivity. Resources live in FastAPI lifespan."""
from collections.abc import AsyncIterator

from fastapi import HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.config import settings


def create_postgres_engine() -> AsyncEngine | None:
    password = settings.POSTGRES_PASSWORD
    if password is None or not password.get_secret_value():
        return None
    url = URL.create(
        "postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=password.get_secret_value(),
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    )
    return create_async_engine(
        url, pool_pre_ping=True, pool_size=5, max_overflow=10,
        pool_timeout=10, connect_args={"timeout": 5},
    )


def create_redis_client() -> Redis:
    return Redis.from_url(
        settings.REDIS_URL, decode_responses=True,
        socket_connect_timeout=3, socket_timeout=3,
        health_check_interval=30,
    )


async def check_postgres(engine: AsyncEngine | None) -> bool:
    if engine is None:
        return False
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        return result.scalar_one() == 1


async def check_redis(client: Redis) -> bool:
    return bool(await client.ping())


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    factory = getattr(request.app.state, "db_sessionmaker", None)
    if factory is None:
        raise HTTPException(503, "PostgreSQL is not configured.")
    async with factory() as session:
        yield session


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
