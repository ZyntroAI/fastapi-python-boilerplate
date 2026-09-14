"""OnSpaceAI main — FastAPI app รวมทุก layer"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app
from pydantic import BaseModel

from app import metrics
from app.cache import MemoryCache
from app.circuit_breaker import CircuitBreaker
from app.config import get_settings
from app.context_compiler import compile_context
from app.fallback_router import FallbackRouter
from app.middleware import AuthMiddleware, RequestContextMiddleware
from app.providers import MockProvider
from app.token_budget import TokenBudget


class AIRequest(BaseModel):
    prompt: str
    system: str = ""
    model: str = "gpt-4o"
    cache: bool = True
    max_tokens: int = 1024


_settings = get_settings()
_cache = MemoryCache(default_ttl=_settings.cache_ttl)
_circuit = CircuitBreaker(_settings.circuit_failure_threshold, _settings.circuit_recovery_seconds)
_router = FallbackRouter(
    [MockProvider(fail_status=None), MockProvider(fail_status=None)],
    _circuit,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/docs")
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(AuthMiddleware)

    @app.get("/health")
    async def health():
        return {"ok": True, "app": settings.app_name, "env": settings.app_env}

    @app.post("/api/ai")
    async def ai(req: AIRequest):
        from app.cache import cache_key

        budget = TokenBudget(req.model)
        context = compile_context(req.system, [{"role": "user", "content": req.prompt}], req.max_tokens)

        if not budget.check(context["estimated_tokens"]):
            raise HTTPException(status_code=413, detail=f"payload too large: {budget.reject_reason(context['estimated_tokens'])}")

        ck = cache_key(req.prompt, req.model, req.max_tokens) if req.cache else None
        if ck:
            cached = await _cache.get(ck)
            if cached:
                metrics.CACHE_HITS.inc()
                return {"ok": True, "cached": True, "content": cached}

        metrics.CACHE_MISSES.inc()

        result = await _router.route(context["system"], context["messages"], req.model, req.max_tokens)
        if result is None:
            raise HTTPException(status_code=503, detail="all providers unavailable (degraded)")

        if ck:
            await _cache.set(ck, result.content)
        return {"ok": True, "cached": False, "content": result.content, "model": result.model}

    app.mount("/metrics", make_asgi_app())
    return app


app = create_app()
