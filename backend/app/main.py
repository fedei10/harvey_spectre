from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import chatbot, health
from app.ai_engineering.agent.graph import build_graph
from app.ai_engineering.agent.checkpoint import postgres_checkpointer
from app.services.PostgreSQL.connection import test_postgres_connection
from app.services.Redis.connection import test_redis_connection
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create/migrate checkpoint tables before accepting chat requests.
    async with postgres_checkpointer(setup=True) as saver:
        app.state.graph = build_graph(saver)
        yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description="LangGrap",
    version=settings.APP_VERSION,
)
app.include_router(chatbot.router, prefix="/v1", tags=["Chatbot"])
app.include_router(health.router, prefix="/v1", tags=["Health"])


@app.get("/test")
def test_connections():
    return {
        "groq_chat": health.check_groq_connection()["status"],
        "redis": test_redis_connection(),
        "postgres": test_postgres_connection(),
    }


@app.get("/")
async def read_root():
    return {"message": "Welcome to My FastAPI Application!"}
