"""Tests: fallback router"""
import pytest

from app.circuit_breaker import CircuitBreaker
from app.fallback_router import FallbackRouter
from app.providers import MockProvider


@pytest.mark.asyncio
async def test_primary_succeeds_no_fallback():
    router = FallbackRouter([MockProvider(), MockProvider()], CircuitBreaker())
    r = await router.route("sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100)
    assert r is not None
    assert "[mock:gpt-4o]" in r.content  # primary ตอบ


@pytest.mark.asyncio
async def test_fallback_on_retryable():
    # primary ล้ม (503 retryable) → secondary สำเร็จ
    router = FallbackRouter(
        [MockProvider(fail_status=503), MockProvider()], CircuitBreaker()
    )
    r = await router.route("sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100)
    assert r is not None
    assert "[mock:gpt-4o]" in r.content


@pytest.mark.asyncio
async def test_all_fail_returns_none_degraded():
    router = FallbackRouter(
        [MockProvider(fail_status=503), MockProvider(fail_status=503)], CircuitBreaker()
    )
    r = await router.route("sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100)
    assert r is None  # degraded


@pytest.mark.asyncio
async def test_non_retryable_stops_no_waste():
    # 400 non-retryable → หยุดทันที ไม่ลอง secondary (ประหยัด cost)
    calls = []
    class Counting(MockProvider):
        async def complete(self, system, messages, model, max_tokens):
            calls.append(1)
            return await super().complete(system, messages, model, max_tokens)

    router = FallbackRouter(
        [MockProvider(fail_status=400), Counting()], CircuitBreaker()
    )
    r = await router.route("sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100)
    assert r is None
    assert len(calls) == 0  # secondary ไม่ถูกเรียก
