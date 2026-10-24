from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.ai_engineering.agent.deps import get_graph
from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import run_chat, stream_chat
from app.services.chat_errors import chat_error

router = APIRouter()
Graph = Annotated[Any, Depends(get_graph)]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, graph: Graph):
    """Non-streaming compatibility endpoint with conversation memory."""
    try:
        reply, conversation_id = await run_chat(
            graph, chat_request.message, chat_request.conversation_id
        )
    except Exception as exc:
        status, detail = chat_error(exc)
        raise HTTPException(status, detail) from exc
    return ChatResponse(response=reply, conversation_id=conversation_id)


@router.post("/chat/stream")
async def chat_stream_endpoint(chat_request: ChatRequest, graph: Graph):
    """Stream AI SDK UI message events, preserving conversation memory."""
    key = settings.GROQ_API_KEY
    if not key or not key.get_secret_value().strip():
        raise HTTPException(503, "GROQ_API_KEY is not configured.")
    return StreamingResponse(
        stream_chat(graph, chat_request.message, chat_request.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "x-vercel-ai-ui-message-stream": "v1",
        },
    )
