from app.api.v1 import health
from fastapi import FastAPI
from app.api.v1 import chatbot
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver



from app.ai_engineering.agent.graph import build_graph
from app.config import settings





@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string(settings.CHECKPOINT_DB) as saver:
        app.state.graph = build_graph(saver)  # compile once
        yield

app = FastAPI(lifespan=lifespan,
    title="My FastAPI Application",
    description="This is a sample FastAPI application.",
    version="1.0.0",

)



app.include_router(chatbot.router, prefix="/v1",tags=["Chatbot"])
app.include_router(health.router, prefix="/v1", tags=["Health"])


@app.get("/test")
def test_connections():
    return {"groq_chat": health.check_groq_connection()["status"]}



@app.get("/")
async def read_root():
    return {"message": "Welcome to My FastAPI Application!"}

