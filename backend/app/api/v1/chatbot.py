from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError, APITimeoutError, APIStatusError

from app.ai_engineering.agent.deps import get_graph
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.codecraft.chat_service import run_chat


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, graph=Depends(get_graph)):
    try:
        response, conversation_id = await run_chat(
            graph, chat_request.message, chat_request.conversation_id
        )
    except APITimeoutError as exc:
        raise HTTPException(504, "CodeCraft request timed out.") from exc
    except APIStatusError as exc:
        if exc.status_code == 402:
            raise HTTPException(
                503, "CodeCraft billing verification failed. Check the provider account balance and payment method."
            ) from exc
        raise HTTPException(502, "CodeCraft chat request failed.") from exc
    except OpenAIError as exc:
        raise HTTPException(502, "CodeCraft chat request failed.") from exc
    except ValueError as exc:
        raise HTTPException(503, "Chat configuration or response is invalid.") from exc
    return ChatResponse(response=response, conversation_id=conversation_id)
