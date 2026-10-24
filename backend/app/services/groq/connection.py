"""Groq connection check using a small chat completion."""

from groq import Groq, APIError
from pydantic import SecretStr

from app.config import settings


def test_groq_connection() -> str:
    api_key = settings.GROQ_API_KEY
    if isinstance(api_key, SecretStr):
        api_key = api_key.get_secret_value()
    if not api_key or not api_key.strip():
        raise ValueError("GROQ_API_KEY is not configured.")

    with Groq(api_key=api_key, timeout=30.0, max_retries=0) as client:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": "Reply with OK."}],
            model=settings.GROQ_MODEL_NAME,
            max_completion_tokens=128,
        )
        if not result.choices or not result.choices[0].message.content:
            import httpx
            raise APIError(
                "Groq returned no chat content.",
                request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
                body=None,
            )
    return "Groq connection successful"
