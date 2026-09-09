"""Redis — แคช + สถานะงาน (fail-open: ถ้า Redis ล่ม ไม่ crash แอป)"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.config.settings import Settings

logger = logging.getLogger("redis")

try:
    import redis.asyncio as aioredis

    _HAS_REDIS = True
except Exception:  # pragma: no cover
    _HAS_REDIS = False


class RedisClient:
    """Client แบบ fail-open — ทุก operation จับข้อยกเว้นแล้ว return fallback"""

    def __init__(self, url: str):
        self._pool = None
        self._url = url
        if _HAS_REDIS:
            try:
                self._pool = aioredis.ConnectionPool.from_url(url, decode_responses=True)
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis init failed: %s", exc)

    async def get_json(self, key: str) -> Optional[Any]:
        if self._pool is None:
            return None
        try:
            from redis import asyncio as aioredis  # noqa: F401

            client = aioredis.Redis(connection_pool=self._pool)
            raw = await client.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:  # pragma: no cover
            logger.warning("Redis get failed (fail-open): %s", exc)
            return None

    async def set_json(self, key: str, value: Any, ttl: int) -> bool:
        if self._pool is None:
            return False
        try:
            from redis import asyncio as aioredis  # noqa: F401

            client = aioredis.Redis(connection_pool=self._pool)
            await client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
            return True
        except Exception as exc:  # pragma: no cover
            logger.warning("Redis set failed (fail-open): %s", exc)
            return False

    async def delete(self, key: str) -> bool:
        if self._pool is None:
            return False
        try:
            from redis import asyncio as aioredis  # noqa: F401

            client = aioredis.Redis(connection_pool=self._pool)
            await client.delete(key)
            return True
        except Exception:  # pragma: no cover
            return False


_cache_client: Optional[RedisClient] = None
_state_client: Optional[RedisClient] = None


def get_cache_client(settings: Settings) -> RedisClient:
    global _cache_client
    if _cache_client is None:
        _cache_client = RedisClient(settings.redis_cache_url)
    return _cache_client


def get_state_client(settings: Settings) -> RedisClient:
    global _state_client
    if _state_client is None:
        _state_client = RedisClient(settings.redis_url)
    return _state_client
