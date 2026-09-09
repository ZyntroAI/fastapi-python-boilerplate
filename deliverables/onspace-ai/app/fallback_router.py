"""Fallback router — Primary → Secondary → Degraded"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app import metrics
from app.circuit_breaker import CircuitBreaker
from app.providers import BaseProvider, ProviderError, ProviderResult

logger = logging.getLogger("fallback")


class FallbackRouter:
    """ลอง provider ตามลำดับ; ล้ม→ตัวถัดไป; ล้มหมด→Degraded

    - Skip provider ที่ circuit breaker เปิด
    - Retryable error → ลองตัวถัดไป
    - Non-retryable (400/401/422) → หยุดทันที (ไม่เสียค่าใช้จ่าย)
    """

    def __init__(self, providers: List[BaseProvider], circuit: CircuitBreaker) -> None:
        self._providers = providers
        self._circuit = circuit

    async def route(self, system: str, messages: List[Dict], model: str, max_tokens: int) -> Optional[ProviderResult]:
        # circuit เปิดทั้งระบบ → degraded
        if not self._circuit.allow_request() and all(not self._circuit.allow_request() for _ in self._providers):
            return None

        for i, provider in enumerate(self._providers):
            if not self._circuit.allow_request():
                continue  # ข้าม provider ที่ circuit เปิด
            try:
                result = await provider.complete(system, messages, model, max_tokens)
                self._circuit.record_success()
                if i > 0:
                    metrics.FALLBACK_TOTAL.labels(self._providers[0].name, provider.name).inc()
                return result
            except ProviderError as exc:
                logger.warning("provider %s failed: %s", provider.name, exc)
                self._circuit.record_failure()
                if not exc.retryable:
                    return None  # non-retryable — ไม่ลอง provider อื่น (blueprint: ไม่เสียค่าใช้จ่าย)
                # retryable → ลองตัวถัดไป
                continue

        # หมดทุกตัว → degraded
        metrics.DEGRADED_TOTAL.inc()
        return None
