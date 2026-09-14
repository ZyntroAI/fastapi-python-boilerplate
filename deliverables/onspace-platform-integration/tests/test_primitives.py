"""Reliability primitive tests — moved unchanged from onspace-ai, plus the new
`route_with_meta` contract that lets callers know which provider answered.
"""
import pytest

from onspace.cache import MemoryCache, RedisCache, cache_key
from onspace.circuit_breaker import CircuitBreaker
from onspace.context import (
    clean_text,
    compile_context,
    deduplicate_messages,
    estimate_tokens,
    trim_history,
)
from onspace.fallback import FallbackRouter
from onspace.providers import MockProvider, ProviderError
from onspace.token_budget import MODEL_LIMITS, TokenBudget


# --- cache ---------------------------------------------------------------

def test_cache_key_deterministic():
    a = cache_key("https://x.com", {"fmt": "json"})
    b = cache_key("https://x.com", {"fmt": "json"})
    assert a == b
    assert a != cache_key("https://x.com", {"fmt": "md"})
    assert a.startswith("onspace:")


def test_cache_key_sorts_keys():
    assert cache_key("a", {"x": 1, "y": 2}) == cache_key("a", {"y": 2, "x": 1})


@pytest.mark.asyncio
async def test_memory_cache_set_get_delete():
    c = MemoryCache(default_ttl=60)
    assert await c.get("k") is None
    await c.set("k", "v")
    assert await c.get("k") == "v"
    await c.delete("k")
    assert await c.get("k") is None


@pytest.mark.asyncio
async def test_memory_cache_expiry():
    import time

    c = MemoryCache(default_ttl=0)
    await c.set("k", "v")
    time.sleep(0.01)
    assert await c.get("k") is None


@pytest.mark.asyncio
async def test_redis_cache_fail_open_no_client():
    rc = RedisCache(client=None, default_ttl=60)
    assert await rc.get("k") is None
    await rc.set("k", "v")
    await rc.delete("k")


# --- circuit breaker -----------------------------------------------------

def test_cb_closed_allows():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    assert cb.state == "CLOSED"
    assert cb.allow_request() is True


def test_cb_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "CLOSED"
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.allow_request() is False


def test_cb_success_resets_failures():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    cb.record_failure()
    assert cb.state == "CLOSED"


def test_cb_half_open_recovers_after_cooldown():
    import time

    cb = CircuitBreaker(failure_threshold=2, recovery_seconds=0.05)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    time.sleep(0.1)
    assert cb.state == "HALF_OPEN"
    assert cb.allow_request() is True


def test_cb_half_open_failure_reopens():
    import time

    cb = CircuitBreaker(failure_threshold=1, recovery_seconds=0.05)
    cb.record_failure()
    assert cb.state == "OPEN"
    time.sleep(0.1)
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.allow_request() is False


# --- context compiler ----------------------------------------------------

def test_clean_text_collapses_whitespace():
    assert clean_text("  a\n\n\n  b  ") == "a\nb"


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") > 0


def test_deduplicate_consecutive_only():
    msgs = [
        {"role": "user", "content": "a"},
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "a"},
    ]
    assert len(deduplicate_messages(msgs)) == 3


def test_trim_history_keeps_last_n():
    msgs = [{"role": "user", "content": f"m{i}"} for i in range(10)]
    out = trim_history(msgs, max_turns=3)
    assert len(out) == 3
    assert out[-1]["content"] == "m9"


def test_compile_context_counts_tokens():
    ctx = compile_context("sys", [{"role": "user", "content": "hello"}], max_tokens=100)
    assert ctx["estimated_tokens"] > 0
    assert ctx["over_budget"] is False
    assert ctx["system"] == "sys"


def test_compile_context_over_budget_flag():
    big = "x" * 5000
    ctx = compile_context(big, [{"role": "user", "content": "y" * 5000}], max_tokens=10)
    assert ctx["over_budget"] is True


# --- token budget --------------------------------------------------------

def test_model_limits_default():
    assert MODEL_LIMITS["default"] == 128000
    assert TokenBudget("gpt-4o").max == 128000
    assert TokenBudget("claude-3-opus").max == 200000


def test_check_within_budget():
    assert TokenBudget("gpt-4o").check(1000) is True


def test_check_over_budget():
    assert TokenBudget("gpt-4o").check(200000) is False


def test_truncate_drops_old_messages():
    b = TokenBudget("mini")
    msgs = [
        {"role": "user", "content": "a" * 100000},
        {"role": "user", "content": "b" * 100000},
        {"role": "user", "content": "c" * 100000},
    ]
    ctx = compile_context("sys", msgs, max_tokens=1000000)
    assert ctx["estimated_tokens"] > b.max
    out = b.truncate(ctx)
    assert out["estimated_tokens"] <= b.max


def test_reject_reason_message():
    assert "exceeds" in TokenBudget("mini").reject_reason(50000)


# --- fallback router -----------------------------------------------------

@pytest.mark.asyncio
async def test_primary_succeeds_no_fallback():
    router = FallbackRouter([MockProvider(), MockProvider()], CircuitBreaker())
    r, name = await router.route_with_meta(
        "sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100
    )
    assert r is not None and name == "mock"
    assert "[mock:gpt-4o]" in r.content


@pytest.mark.asyncio
async def test_fallback_on_retryable():
    router = FallbackRouter([MockProvider(fail_status=503), MockProvider()], CircuitBreaker())
    r, name = await router.route_with_meta(
        "sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100
    )
    assert r is not None and name == "mock"


@pytest.mark.asyncio
async def test_all_fail_returns_none_degraded():
    router = FallbackRouter(
        [MockProvider(fail_status=503), MockProvider(fail_status=503)], CircuitBreaker()
    )
    r, name = await router.route_with_meta(
        "sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100
    )
    assert r is None and name == ""


@pytest.mark.asyncio
async def test_non_retryable_stops_no_waste():
    calls = []

    class Counting(MockProvider):
        async def complete(self, system, messages, model, max_tokens):
            calls.append(1)
            return await super().complete(system, messages, model, max_tokens)

    router = FallbackRouter([MockProvider(fail_status=400), Counting()], CircuitBreaker())
    r, name = await router.route_with_meta(
        "sys", [{"role": "user", "content": "hi"}], "gpt-4o", 100
    )
    assert r is None and name == ""
    assert len(calls) == 0


# --- provider error model ------------------------------------------------

def test_provider_error_retryable_classification():
    assert ProviderError(status=503).retryable is True
    assert ProviderError(status=429).retryable is True
    assert ProviderError(status=401).retryable is False
    assert ProviderError(status=400).retryable is False
