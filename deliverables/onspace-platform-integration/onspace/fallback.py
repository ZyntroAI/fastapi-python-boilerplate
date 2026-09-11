"""Fallback router — walk providers in order, degrade gracefully.

The router is deliberately provider-agnostic: it takes an ordered list and a
shared circuit breaker, so ordering (OpenAI → Anthropic → Google → degraded)
is a wiring decision, not a code change.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from . import metrics
from .circuit_breaker import CircuitBreaker
from .providers import BaseProvider, ProviderError, ProviderResult

logger = logging.getLogger("onspace.fallback")


class FallbackRouter:
    """Try providers in order; skip tripped ones; stop early on hard errors.

    - Skips providers whose circuit breaker is open
    - Retryable error → try the next provider
    - Non-retryable error (400/401/403/422) → stop (do not waste spend)
    - All failed → return None (degraded)
    """

    def __init__(self, providers: List[BaseProvider], circuit: CircuitBreaker) -> None:
        self._providers = providers
        self._circuit = circuit

    @property
    def providers(self) -> List[BaseProvider]:
        return list(self._providers)

    async def route(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> Optional[ProviderResult]:
        return await self.route_with_meta(system, messages, model, max_tokens)

    async def route_with_meta(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> Tuple[Optional[ProviderResult], str]:
        """Return (result, provider_name). provider_name is '' when degraded."""
        if not self._circuit.allow_request() and all(
            not self._circuit.allow_request() for _ in self._providers
        ):
            return None, ""

        for i, provider in enumerate(self._providers):
            if not self._circuit.allow_request():
                continue  # skip provider while the circuit is open
            try:
                result = await provider.complete(system, messages, model, max_tokens)
                self._circuit.record_success()
                if i > 0:
                    metrics.FALLBACK_TOTAL.labels(self._providers[0].name, provider.name).inc()
                return result, provider.name
            except ProviderError as exc:
                logger.warning("provider %s failed: %s", provider.name, exc)
                self._circuit.record_failure()
                if not exc.retryable:
                    return None, ""  # non-retryable — do not fall through
                continue

        metrics.DEGRADED_TOTAL.inc()
        return None, ""
