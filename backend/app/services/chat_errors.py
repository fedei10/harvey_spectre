"""Safe, shared error messages for JSON and streaming chat."""
from groq import AuthenticationError, APITimeoutError, GroqError, RateLimitError


def chat_error(exc: Exception) -> tuple[int, str]:
    if isinstance(exc, APITimeoutError):
        return 504, "Groq request timed out."
    if isinstance(exc, AuthenticationError):
        return 503, "Groq rejected the configured API key."
    if isinstance(exc, RateLimitError):
        return 503, "Groq rate limit or quota exceeded."
    if isinstance(exc, GroqError):
        return 502, "Groq chat request failed."
    if isinstance(exc, ValueError):
        return 503, "Chat configuration or response is invalid."
    return 500, "Chat failed. Please try again."
