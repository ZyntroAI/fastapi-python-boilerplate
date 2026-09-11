"""Middleware — request id, latency, metrics, and optional API-key gate.

The API-key gate is opt-in (only active when ONSPACE_API_KEY is set) so the
integration never fights the core app's own OAuth/JWT auth.
"""
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from . import metrics
from .config import get_onspace_settings

_EXEMPT = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID, record latency, and count requests by status."""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            metrics.API_REQUESTS.labels(request.url.path, "500").inc()
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "internal", "message": str(exc)}},
            )
        latency = time.monotonic() - start
        metrics.LATENCY.labels(request.url.path).observe(latency)
        metrics.API_REQUESTS.labels(request.url.path, str(response.status_code)).inc()
        response.headers["X-Request-ID"] = rid
        return response


class OnSpaceAuthMiddleware(BaseHTTPMiddleware):
    """Optional X-API-Key check. No-op when no key is configured."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in _EXEMPT:
            return await call_next(request)
        settings = get_onspace_settings()
        if settings.api_key and not path.startswith("/api/v1/"):
            key = request.headers.get("x-api-key", "")
            if key != settings.api_key:
                return JSONResponse(
                    status_code=401,
                    content={
                        "ok": False,
                        "error": {"code": "unauthorized", "message": "invalid api key"},
                    },
                )
        return await call_next(request)
