import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.ai_engineering.agent.graph import build_graph
from app.api.v1 import chatbot, health
from app.config import settings
from app.core.connecte import (
    check_postgres, check_redis, create_postgres_engine, create_redis_client,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_postgres_engine()
    redis = create_redis_client()
    app.state.postgres_engine = engine
    app.state.redis = redis
    app.state.db_sessionmaker = (
        async_sessionmaker(engine, expire_on_commit=False)
        if engine is not None else None
    )
    try:
        # Preserve SQLite checkpoints until the separate migration step.
        async with AsyncSqliteSaver.from_conn_string(settings.CHECKPOINT_DB) as saver:
            app.state.graph = build_graph(saver)
            yield
    finally:
        if engine is not None:
            await engine.dispose()
        await redis.aclose()

app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description="FastAPI chatbot with PostgreSQL and Redis connections.",
    version=settings.APP_VERSION,
)
app.include_router(chatbot.router, prefix="/v1", tags=["Chatbot"])
app.include_router(health.router, prefix="/v1", tags=["Health"])

async def _probe(name: str, operation) -> str:
    try:
        ok = await asyncio.wait_for(operation, timeout=6)
        return "connected" if ok else "disconnected"
    except Exception:
        logger.warning("%s connection check failed", name)
        return "disconnected"

@app.get("/test")
async def test_connections(request: Request):
    engine = getattr(request.app.state, "postgres_engine", None)
    redis = getattr(request.app.state, "redis", None)
    postgres_status = (
        await _probe("postgres", check_postgres(engine))
        if engine is not None else "not_configured"
    )
    redis_status = (
        await _probe("redis", check_redis(redis))
        if redis is not None else "not_configured"
    )
    services = {"postgres": postgres_status, "redis": redis_status}
    status = 200 if all(s == "connected" for s in services.values()) else 503
    return JSONResponse(status_code=status, content=services)

@app.get("/")
async def read_root():
    return {"message": "Welcome to My FastAPI Application!"}
