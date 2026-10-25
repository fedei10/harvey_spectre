
import logging

from openai import OpenAI, OpenAIError
from pydantic import SecretStr

from app.config import settings


logger = logging.getLogger(__name__)

BASE_URL = "https://codecraftapi.com/v1"


def get_codecraft_connection() -> OpenAI:
    """Create and return a CodeCraft API client."""

    api_key = settings.OPENAI_API_KEY

    # Handle Pydantic SecretStr
    if isinstance(api_key, SecretStr):
        api_key = api_key.get_secret_value()

    if not api_key or not api_key.strip():
        raise ValueError("OPENAI_API_KEY is not configured.")

    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL,
        timeout=30.0,
        max_retries=2,
    )

    return client


def get_models() -> list[dict]:
    """Retrieve all available CodeCraft models."""

    with get_codecraft_connection() as client:
        response = client.models.list()

    return [
        model.model_dump()
        for model in response.data
    ]


def test_connection() -> bool:
    """Test CodeCraft API connectivity and model-list access."""

    try:
        with get_codecraft_connection() as client:
            client.models.list()

        logger.info("CodeCraft API connection successful.")

        return True

    except (OpenAIError, ValueError) as e:
        logger.error("CodeCraft connection failed: %s", e)

        return False
