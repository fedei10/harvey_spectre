from fastapi import APIRouter, HTTPException
from openai import OpenAIError, APITimeoutError

from app.services.codecraft.connection import get_models


router = APIRouter(prefix="/health", tags=["Health"])


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
