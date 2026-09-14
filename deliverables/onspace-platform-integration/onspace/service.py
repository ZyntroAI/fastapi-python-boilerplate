"""OnSpaceAIService — the reusable AI infrastructure layer.

This is the whole point of the migration: the reliability pipeline (cache →
context compiler → token budget → circuit breaker → provider → fallback) is a
plain async service with NO FastAPI imports. REST routes, GraphQL resolvers,
background workers, and a CLI all call the same `generate()`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from . import metrics
from .cache import MemoryCache, cache_key
from .config import OnSpaceSettings, get_onspace_settings
from .context import compile_context
from .fallback import FallbackRouter
from .models import AIRequest, AIResponse, Message
from .token_budget import TokenBudget


class PayloadTooLarge(Exception):
    """Raised when the compiled context exceeds the model's token ceiling."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AllProvidersUnavailable(Exception):
    """Raised when the provider chain is exhausted and the system is degraded."""

    def __init__(self, message: str = "all providers unavailable (degraded)") -> None:
        super().__init__(message)
        self.message = message


class OnSpaceAIService:
    """Stateless-per-call AI engine; dependencies are injected for testability."""

    def __init__(
        self,
        router: FallbackRouter,
        cache=None,
        settings: Optional[OnSpaceSettings] = None,
    ) -> None:
        self._router = router
        self._cache = cache if cache is not None else MemoryCache()
        self._settings = settings or get_onspace_settings()

    @property
    def settings(self) -> OnSpaceSettings:
        return self._settings

    def _to_messages(self, request: AIRequest) -> List[Dict]:
        if request.messages:
            return [m.model_dump() for m in request.messages]
        return [{"role": "user", "content": request.prompt}]

    async def generate(self, request: AIRequest) -> AIResponse:
        budget = TokenBudget(request.model)
        context = compile_context(request.system, self._to_messages(request), request.max_tokens)

        if not budget.check(context["estimated_tokens"]):
            raise PayloadTooLarge(budget.reject_reason(context["estimated_tokens"]))

        ck = cache_key(request.prompt, request.model, request.max_tokens) if request.cache else None
        if ck:
            cached = await self._cache.get(ck)
            if cached:
                metrics.CACHE_HITS.inc()
                return AIResponse(
                    ok=True,
                    cached=True,
                    content=cached,
                    model=request.model,
                    provider="cache",
                    estimated_tokens=context["estimated_tokens"],
                )

        metrics.CACHE_MISSES.inc()

        result, provider = await self._router.route_with_meta(
            context["system"], context["messages"], request.model, request.max_tokens
        )
        if result is None:
            raise AllProvidersUnavailable()

        if ck:
            await self._cache.set(ck, result.content)

        return AIResponse(
            ok=True,
            cached=False,
            content=result.content,
            model=result.model,
            provider=provider,
            tokens_used=result.tokens_used,
            estimated_tokens=context["estimated_tokens"],
        )
