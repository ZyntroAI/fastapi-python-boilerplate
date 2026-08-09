# app/core/cache.py
import redis.asyncio as redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=5,      # Fail fast
    socket_connect_timeout=2,
    max_connections=50,    # Connection pool size
)

async def get_cached(key: str):
    return await redis_client.get(key)

async def set_cached(key: str, value: str, ttl: int = 60):
    await redis_client.setex(key, ttl, value)
