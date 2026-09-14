"""Redis infrastructure: async client + cache helpers.

Kept fail-open: when Redis is unavailable, cache lookups miss and writes no-op
rather than raising, so an outage degrades performance instead of breaking the
API (matching the user's graceful-degradation pattern).
"""
from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

settings = get_settings()
_redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> Redis:
    return _redis


async def cache_get(key: str) -> Any | None:
    try:
        raw = await _redis.get(key)
    except RedisError:
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


async def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    try:
        await _redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except (RedisError, TypeError):
        return
