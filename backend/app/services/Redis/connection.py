import redis

from app.config import settings


def get_redis_connection():
    return redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        username="default",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


def check_redis_connection():
    try:
        with get_redis_connection() as client:
            if client.ping():
                return "✅ Redis Connected Successfully"
            return "❌ Redis Connection Failed: no PONG response"
    except redis.RedisError as exc:
        return f"❌ Redis Connection Failed: {type(exc).__name__}"


# Keep the original public name available for existing imports.
test_redis_connection = check_redis_connection
