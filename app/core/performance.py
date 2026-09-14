import time
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.config import settings

class PerformanceManager:
    """Central performance control — cache + budget + metrics"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._request_counts: dict[str, int] = {}
        self._token_usage: dict[str, int] = {}

    async def connect(self):
        """Initialize Redis connection"""
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)

    async def close(self):
        """Cleanup"""
        if self.redis:
            await self.redis.close()

    # ── Caching ──
    async def get_cache(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set_cache(self, key: str, value: Any, ttl: int = 300):
        """Cache with TTL — default 5 minutes"""
        if self.redis:
            await self.redis.setex(key, ttl, value)

    # ── Rate Limiting ──
    async def check_rate_limit(self, user_id: str, limit: int = 100, window: int = 60) -> bool:
        """Per-user rate limit — requests per window seconds"""
        key = f"rate:{user_id}:{int(time.time() // window)}"
        if not self.redis:
            self._request_counts[user_id] = self._request_counts.get(user_id, 0) + 1
            return self._request_counts[user_id] <= limit
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)
        return current <= limit

    # ── Token Budget ──
    async def check_budget(self, user_id: str, tokens: int, daily_limit: int = 100000) -> tuple[bool, int]:
        """Enforce daily token budget"""
        key = f"budget:{user_id}:{datetime.utcnow().strftime('%Y%m%d')}"
        if not self.redis:
            used = self._token_usage.get(user_id, 0)
            self._token_usage[user_id] = used + tokens
            return (used + tokens) <= daily_limit, daily_limit - (used + tokens)
        used = await self.redis.incrby(key, tokens)
        await self.redis.expire(key, 86400)
        return used <= daily_limit, daily_limit - used

    # ── Metrics ──
    def track_latency(self, endpoint: str, duration_ms: float):
        """Record endpoint latency — for monitoring"""
        # Push to Prometheus / metrics system
        pass


# Global instance
performance = PerformanceManager()

# ── Decorators ──
def cache_result(ttl: int = 300):
    """Cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"cache:{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = await performance.get_cache(cache_key)
            if cached:
                return cached
            result = await func(*args, **kwargs)
            await performance.set_cache(cache_key, str(result), ttl)
            return result
        return wrapper
    return decorator

def track_performance(endpoint: str):
    """Auto-track latency for endpoints"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                latency = (time.perf_counter() - start) * 1000
                performance.track_latency(endpoint, latency)
        return wrapper
    return decorator
