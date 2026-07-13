import redis.asyncio as redis
from typing import AsyncGenerator
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    FastAPI dependency that yields the async Redis client instance.
    """
    yield redis_client