"""Tests: cache key + memory cache"""
import pytest

from app.cache import MemoryCache, RedisCache, cache_key


def test_cache_key_deterministic():
    a = cache_key("https://x.com", {"fmt": "json"})
    b = cache_key("https://x.com", {"fmt": "json"})
    assert a == b
    c = cache_key("https://x.com", {"fmt": "md"})
    assert a != c
    assert a.startswith("onspace:")


def test_cache_key_sorts_keys():
    assert cache_key("a", {"x": 1, "y": 2}) == cache_key("a", {"y": 2, "x": 1})


@pytest.mark.asyncio
async def test_memory_cache_set_get_delete():
    c = MemoryCache(default_ttl=60)
    assert await c.get("k") is None  # miss
    await c.set("k", "v")
    assert await c.get("k") == "v"
    await c.delete("k")
    assert await c.get("k") is None


@pytest.mark.asyncio
async def test_memory_cache_expiry():
    c = MemoryCache(default_ttl=0)  # หมดอายุทันที
    await c.set("k", "v")
    import time
    time.sleep(0.01)
    assert await c.get("k") is None


@pytest.mark.asyncio
async def test_redis_cache_fail_open_no_client():
    # RedisCache ไม่มี client → get/set เป็น no-op ไม่ crash
    rc = RedisCache(client=None, default_ttl=60)
    assert await rc.get("k") is None
    await rc.set("k", "v")  # ไม่ raise
    await rc.delete("k")
