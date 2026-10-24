import json
import logging
from collections.abc import AsyncIterator
from uuid import uuid4

from langchain_core.messages import AIMessageChunk, HumanMessage

from app.services.chat_errors import chat_error

logger = logging.getLogger(__name__)


def _config(conversation_id: str) -> dict:
    return {"configurable": {"thread_id": conversation_id}}


async def run_chat(graph, message: str, conversation_id: str | None) -> tuple[str, str]:
    conversation_id = conversation_id or str(uuid4())

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        _config(conversation_id),
    )
    response = result["messages"][-1].text
    if not response.strip():
        raise ValueError("The model returned an empty chat response.")
    return response, conversation_id


def _event(payload: dict) -> str:
    # JSON escaping preserves newlines and Unicode across SSE frames.
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_chat(graph, message: str, conversation_id: str | None) -> AsyncIterator[str]:
    conversation_id = conversation_id or str(uuid4())
    text_id = str(uuid4())
    yield _event({"type": "start", "messageId": str(uuid4()),
                  "messageMetadata": {"conversationId": conversation_id}})
    yield _event({"type": "text-start", "id": text_id})
    has_text = False
    try:
        async for chunk, meta in graph.astream(
            {"messages": [HumanMessage(content=message)]},
            _config(conversation_id),
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk) and meta.get("langgraph_node") == "llm":
                text = chunk.text
                if text:
                    has_text = True
                    yield _event({"type": "text-delta", "id": text_id, "delta": text})
        if not has_text:
            raise ValueError("The model returned an empty chat response.")
    except Exception as exc:
        logger.warning("Streaming chat failed (%s)", type(exc).__name__)
        _, detail = chat_error(exc)
        yield _event({"type": "error", "errorText": detail})
        yield _event({"type": "text-end", "id": text_id})
        yield _event({"type": "finish", "finishReason": "error"})
    else:
        yield _event({"type": "text-end", "id": text_id})
        yield _event({"type": "finish", "finishReason": "stop"})
    yield "data: [DONE]\n\n"
