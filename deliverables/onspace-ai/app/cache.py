"""Cache — Redis + hash key + TTL (fail-open ถ้า Redis ล่ม)"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional


def cache_key(*parts: Any) -> str:
    """สร้าง deterministic SHA-256 key จากส่วนประกอบ (URL/options)"""
    blob = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "onspace:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


class RedisCache:
    """Cache wrapper — fail-open: ถ้า Redis ล่ม ให้ cache miss (ไม่ crash)"""

    def __init__(self, client: Optional[Any] = None, default_ttl: int = 300) -> None:
        self._redis = client
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Optional[str]:
        if self._redis is None:
            return None
        try:
            val = await self._redis.get(key)
            return val.decode() if isinstance(val, bytes) else val
        except Exception:
            return None  # fail-open

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.set(key, value, ex=ttl if ttl is not None else self._default_ttl)
        except Exception:
            pass  # fail-open

    async def delete(self, key: str) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.delete(key)
        except Exception:
            pass  # fail-open


class MemoryCache:
    """Cache หน่วยความจำ (สำหรับทดสอบ / ไม่มี Redis)"""

    def __init__(self, default_ttl: int = 300) -> None:
        self._default_ttl = default_ttl
        self._store: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            return None
        value, expire = item
        if expire < __import__("time").time():
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        import time

        t = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.time() + t)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
