"""Isolated FastAPI app factory for the OnSpaceAI integration.

Mounted into the core app, or run standalone for local development. Kept in
one function so there is exactly one place that wires routes + middleware.
"""
from __future__ import annotations

from fastapi import FastAPI

from . import __name__ as _pkg
from .api import get_onspace_service, metrics_app, router
from .config import get_onspace_settings
from .middleware import OnSpaceAuthMiddleware, RequestContextMiddleware
from .service import OnSpaceAIService


def create_onspace_app(service: OnSpaceAIService | None = None, with_metrics: bool = True) -> FastAPI:
    """Build a standalone OnSpaceAI app. Pass `service` to inject a configured engine."""
    settings = get_onspace_settings()
    app = FastAPI(title=settings.app_name, version="1.1.0", docs_url="/docs")
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(OnSpaceAuthMiddleware)

    if service is not None:
        from .api import set_onspace_service

        set_onspace_service(service)

    app.include_router(router, prefix="/api/v1/ai")
    if with_metrics:
        app.mount("/metrics", metrics_app())
    return app


def register_onspace(app: FastAPI, service: OnSpaceAIService | None = None, prefix: str = "/api/v1/ai") -> FastAPI:
    """Attach the OnSpaceAI routes to an existing FastAPI app (the integration path)."""
    if service is not None:
        from .api import set_onspace_service

        set_onspace_service(service)
    app.include_router(router, prefix=prefix)
    return app


__all__ = ["create_onspace_app", "register_onspace", "get_onspace_service"]
