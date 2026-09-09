"""Middleware — auth + request-id + error format"""
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app import metrics
from app.config import get_settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    """เพิ่ม X-Request-ID + วัด latency + นับ request"""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            metrics.API_REQUESTS.labels(request.url.path, "500").inc()
            return JSONResponse(status_code=500, content={"ok": False, "error": {"code": "internal", "message": str(exc)}})
        latency = time.monotonic() - start
        metrics.LATENCY.labels(request.url.path).observe(latency)
        metrics.API_REQUESTS.labels(request.url.path, str(response.status_code)).inc()
        response.headers["X-Request-ID"] = rid
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """ตรวจ X-API-Key — ข้าม /health และ /metrics"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in ("/health", "/metrics", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)
        settings = get_settings()
        if settings.api_key:
            key = request.headers.get("x-api-key", "")
            if key != settings.api_key:
                return JSONResponse(status_code=401, content={"ok": False, "error": {"code": "unauthorized", "message": "invalid api key"}})
        return await call_next(request)
