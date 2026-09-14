"""Composition root — build the OnSpaceAI service from settings.

Keeping wiring here means the HTTP layer, GraphQL, workers, and CLI all get
the same configured engine without duplicating provider setup.
"""
from __future__ import annotations

from typing import Optional

from .cache import MemoryCache, RedisCache
from .circuit_breaker import CircuitBreaker
from .config import OnSpaceSettings, get_onspace_settings
from .fallback import FallbackRouter
from .providers import (
    AnthropicProvider,
    BaseProvider,
    GoogleProvider,
    MockProvider,
    OpenAIProvider,
)
from .service import OnSpaceAIService


def build_providers(settings: OnSpaceSettings) -> list[BaseProvider]:
    """Ordered provider chain: real vendors first, mock as a last-resort local echo.

    Providers whose key is absent fail fast with a non-retryable 401, so the
    router stops rather than silently degrading — that is the correctness we
    want in production. Set ONSPACE_ALLOW_MOCK=1 to append the mock.
    """
    chain: list[BaseProvider] = []
    if settings.openai_api_key:
        chain.append(OpenAIProvider(api_key=settings.openai_api_key))
    if settings.anthropic_api_key:
        chain.append(AnthropicProvider(api_key=settings.anthropic_api_key))
    if settings.google_api_key:
        chain.append(GoogleProvider(api_key=settings.google_api_key))
    if not chain:
        # No credentials configured → local/dev mode.
        chain.append(MockProvider())
    return chain


def build_service(settings: Optional[OnSpaceSettings] = None, cache_backend=None) -> OnSpaceAIService:
    settings = settings or get_onspace_settings()
    cache = cache_backend if cache_backend is not None else MemoryCache(default_ttl=settings.cache_ttl)
    circuit = CircuitBreaker(
        settings.circuit_failure_threshold, settings.circuit_recovery_seconds
    )
    router = FallbackRouter(build_providers(settings), circuit)
    return OnSpaceAIService(router=router, cache=cache, settings=settings)


def build_redis_cache(settings: Optional[OnSpaceSettings] = None):
    """Best-effort Redis cache. Returns MemoryCache when redis is unavailable."""
    settings = settings or get_onspace_settings()
    try:
        from redis.asyncio import from_url as redis_from_url

        client = redis_from_url(settings.redis_url, decode_responses=False)
        return RedisCache(client=client, default_ttl=settings.cache_ttl)
    except Exception:
        return MemoryCache(default_ttl=settings.cache_ttl)


__all__ = ["build_providers", "build_service", "build_redis_cache"]
