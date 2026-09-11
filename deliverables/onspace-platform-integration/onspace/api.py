"""Thin HTTP layer over OnSpaceAIService — no business logic lives here."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import make_asgi_app

from .config import OnSpaceSettings, get_onspace_settings
from .models import AIRequest, AIResponse
from .service import (
    AllProvidersUnavailable,
    OnSpaceAIService,
    PayloadTooLarge,
)

router = APIRouter(tags=["AI"])

# Process-wide default service. Overridden in tests / workers via dependency_overrides.
_service: OnSpaceAIService | None = None


def get_onspace_service() -> OnSpaceAIService:
    """Dependency provider — import-time lazy so routes never fail to load."""
    global _service
    if _service is None:
        from .factory import build_service

        _service = build_service()
    return _service


def set_onspace_service(service: OnSpaceAIService) -> None:
    """Inject a service instance (used by the app factory, tests, and workers)."""
    global _service
    _service = service


@router.get("/health")
async def health(settings: OnSpaceSettings = Depends(get_onspace_settings)):
    return {"ok": True, "app": settings.app_name, "env": settings.app_env}


@router.post("/generate", response_model=AIResponse)
async def generate(
    request: AIRequest,
    service: OnSpaceAIService = Depends(get_onspace_service),
) -> AIResponse:
    try:
        return await service.generate(request)
    except PayloadTooLarge as exc:
        raise HTTPException(status_code=413, detail=f"payload too large: {exc.message}")
    except AllProvidersUnavailable as exc:
        raise HTTPException(status_code=503, detail=exc.message)


def metrics_app():
    """ASGI app exposing the Prometheus registry — mount at /metrics."""
    return make_asgi_app()
