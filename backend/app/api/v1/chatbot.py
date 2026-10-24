from fastapi import APIRouter, Depends, HTTPException
from groq import GroqError, APITimeoutError, AuthenticationError, RateLimitError

from app.ai_engineering.agent.deps import get_graph
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import run_chat


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, graph=Depends(get_graph)):
    try:
        response, conversation_id = await run_chat(
            graph, chat_request.message, chat_request.conversation_id
        )
    except APITimeoutError as exc:
        raise HTTPException(504, "Groq request timed out.") from exc
    except AuthenticationError as exc:
        raise HTTPException(503, "Groq rejected the configured API key.") from exc
    except RateLimitError as exc:
        raise HTTPException(503, "Groq rate limit or quota exceeded.") from exc
    except GroqError as exc:
        raise HTTPException(502, "Groq chat request failed.") from exc
    except ValueError as exc:
        raise HTTPException(503, "Chat configuration or response is invalid.") from exc
    return ChatResponse(response=response, conversation_id=conversation_id)
