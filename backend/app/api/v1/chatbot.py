from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.deps import get_graph
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import run_chat, stream_chat

router = APIRouter()

Graph = Annotated[Any, Depends(get_graph)]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, graph: Graph):
    """Chat endpoint with conversation memory."""
    reply, conversation_id = await run_chat(
        graph, chat_request.message, chat_request.conversation_id
    )
    return ChatResponse(response=reply, conversation_id=conversation_id)


@router.post("/chat/stream")
async def chat_stream_endpoint(chat_request: ChatRequest, graph: Graph):
    """Server-sent events stream of the model's tokens."""
    return StreamingResponse(
        stream_chat(graph, chat_request.message, chat_request.conversation_id),
        media_type="text/event-stream",
    )