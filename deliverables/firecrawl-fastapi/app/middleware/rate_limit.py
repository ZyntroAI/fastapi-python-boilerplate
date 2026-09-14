"""Rate limit middleware — จำกัดคำขอต่อนาที (fail-open ถ้า Redis ล่ม)"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import Settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit แบบ sliding window ผ่าน Redis (fail-open)

    ใช้ Redis ที่ state client; ถ้า Redis ล่ม → ปล่อยผ่าน (fail-open) ตาม blueprint
    """

    def __init__(self, app, settings: Settings, redis_client=None):
        super().__init__(app)
        self._settings = settings
        self._redis = redis_client

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # กำหนด quota ตาม endpoint
        if path.endswith("/scrape"):
            limit = self._settings.rate_limit_scrape
        elif path.endswith("/crawl"):
            limit = self._settings.rate_limit_crawl
        else:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        window = 60
        key = f"rl:{path}:{client_ip}:{int(time.time()) // window}"

        if self._redis is not None:
            try:
                from redis import asyncio as aioredis  # noqa

                count = await self._redis.incr(key)
                if count == 1:
                    await self._redis.expire(key, window)
                if count > limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "rate limit exceeded", "limit": limit},
                    )
            except Exception:
                # fail-open: Redis ล่ม → ปล่อยผ่าน
                pass

        return await call_next(request)
