from fastapi import APIRouter, HTTPException
from openai import OpenAIError, APITimeoutError
import groq
from app.services.groq.connection import test_groq_connection

from app.services.codecraft.connection import get_models


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/GROQ")
def check_groq_connection():
    try:
        return {"status": test_groq_connection()}
    except ValueError as exc:
        raise HTTPException(503, "GROQ_API_KEY is not configured.") from exc
    except groq.AuthenticationError as exc:
        raise HTTPException(503, "Groq rejected the configured API key.") from exc
    except groq.RateLimitError as exc:
        raise HTTPException(503, "Groq rate limit or quota exceeded.") from exc
    except groq.APITimeoutError as exc:
        raise HTTPException(504, "Groq request timed out.") from exc
    except groq.GroqError as exc:
        raise HTTPException(502, "Groq connection test failed.") from exc


def _fetch_models():
    try:
        return get_models()
    except ValueError as exc:
        raise HTTPException(503, "OPENAI_API_KEY is not configured.") from exc
    except APITimeoutError as exc:
        raise HTTPException(504, "CodeCraft request timed out.") from exc
    except OpenAIError as exc:
        raise HTTPException(502, "CodeCraft models request failed.") from exc


@router.get("/CODE_CRAFT")
def check_codecraft_api_key():
    _fetch_models()
    return {"status": "CodeCraft connection successful."}


@router.get("/CODE_CRAFT/GET_MODELS")
def get_codecraft_models():
    return {"status": "success", "models": _fetch_models()}
