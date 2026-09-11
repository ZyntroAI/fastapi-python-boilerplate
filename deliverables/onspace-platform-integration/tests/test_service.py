"""Service-layer tests — the engine must work with NO FastAPI import.

These lock in the core claim of the migration: OnSpaceAI is usable as an
infrastructure service, callable from REST, GraphQL, a worker, or a CLI.
"""
import pytest

from onspace.cache import MemoryCache
from onspace.circuit_breaker import CircuitBreaker
from onspace.fallback import FallbackRouter
from onspace.models import AIRequest, Message
from onspace.providers import MockProvider
from onspace.service import (
    AllProvidersUnavailable,
    OnSpaceAIService,
    PayloadTooLarge,
)


def make_service(providers=None, cache=None, circuit=None):
    providers = providers or [MockProvider()]
    circuit = circuit or CircuitBreaker()
    router = FallbackRouter(providers, circuit)
    return OnSpaceAIService(router=router, cache=cache or MemoryCache(default_ttl=60))


@pytest.mark.asyncio
async def test_generate_returns_content_and_provider():
    svc = make_service()
    r = await svc.generate(AIRequest(prompt="hello"))
    assert r.ok is True
    assert r.cached is False
    assert r.provider == "mock"
    assert "[mock:gpt-4o]" in r.content
    assert r.estimated_tokens > 0


@pytest.mark.asyncio
async def test_generate_cache_hit_on_second_call():
    svc = make_service()
    req = AIRequest(prompt="cache me", model="gpt-4o")
    first = await svc.generate(req)
    second = await svc.generate(req)
    assert first.cached is False
    assert second.cached is True
    assert second.provider == "cache"
    assert second.content == first.content


@pytest.mark.asyncio
async def test_generate_cache_disabled_never_hits():
    svc = make_service()
    req = AIRequest(prompt="no cache", cache=False)
    await svc.generate(req)
    r = await svc.generate(req)
    assert r.cached is False


@pytest.mark.asyncio
async def test_generate_rejects_oversized_payload():
    svc = make_service()
    with pytest.raises(PayloadTooLarge) as exc:
        await svc.generate(AIRequest(prompt="x" * 200000, model="mini"))
    assert "exceeds" in exc.value.message


@pytest.mark.asyncio
async def test_generate_raises_when_all_providers_fail():
    svc = make_service([MockProvider(fail_status=503), MockProvider(fail_status=503)])
    with pytest.raises(AllProvidersUnavailable):
        await svc.generate(AIRequest(prompt="hi"))


@pytest.mark.asyncio
async def test_generate_uses_full_message_history_when_given():
    svc = make_service()
    req = AIRequest(
        prompt="ignored",
        messages=[
            Message(role="user", content="first"),
            Message(role="assistant", content="reply"),
            Message(role="user", content="second"),
        ],
    )
    r = await svc.generate(req)
    assert "second" in r.content


@pytest.mark.asyncio
async def test_fallback_records_provider_that_answered():
    svc = make_service([MockProvider(fail_status=503), MockProvider()])
    r = await svc.generate(AIRequest(prompt="hi"))
    assert r.ok is True
    assert r.provider == "mock"
