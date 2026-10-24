from collections.abc import AsyncIterator
from uuid import uuid4

from langchain_core.messages import AIMessageChunk, HumanMessage


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


async def stream_chat(graph, message: str, conversation_id: str | None) -> AsyncIterator[str]:
    conversation_id = conversation_id or str(uuid4())

    # First event tells the client which conversation this is
    yield f"event: meta\ndata: {conversation_id}\n\n"

    async for chunk, meta in graph.astream(
        {"messages": [HumanMessage(content=message)]},
        _config(conversation_id),
        stream_mode="messages",
    ):
        if (
            isinstance(chunk, AIMessageChunk)
            and chunk.content
            and meta.get("langgraph_node") == "llm"
        ):
            yield f"data: {chunk.content}\n\n"

    yield "event: done\ndata: [DONE]\n\n"
