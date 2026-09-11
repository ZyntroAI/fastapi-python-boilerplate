"""OnSpaceAI integration — reusable AI infrastructure for the FastAPI core.

Public surface:

    from app.integrations.onspace import build_service, AIRequest

    service = build_service()
    response = await service.generate(AIRequest(prompt="hello"))
"""
from __future__ import annotations

from .cache import MemoryCache, RedisCache, cache_key
from .circuit_breaker import CircuitBreaker
from .config import OnSpaceSettings, get_onspace_settings
from .context import compile_context, estimate_tokens
from .factory import build_providers, build_redis_cache, build_service
from .fallback import FallbackRouter
from .models import AIRequest, AIResponse, Message
from .service import AllProvidersUnavailable, OnSpaceAIService, PayloadTooLarge
from .token_budget import MODEL_LIMITS, TokenBudget

__all__ = [
    "AIRequest",
    "AIResponse",
    "AllProvidersUnavailable",
    "CircuitBreaker",
    "FallbackRouter",
    "MODEL_LIMITS",
    "MemoryCache",
    "Message",
    "OnSpaceAIService",
    "OnSpaceSettings",
    "PayloadTooLarge",
    "RedisCache",
    "TokenBudget",
    "build_providers",
    "build_redis_cache",
    "build_service",
    "cache_key",
    "compile_context",
    "estimate_tokens",
    "get_onspace_settings",
]
