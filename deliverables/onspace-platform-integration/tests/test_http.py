"""HTTP-layer tests — proves the FastAPI route is a thin wrapper over the service."""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from onspace.api import set_onspace_service
from onspace.app import create_onspace_app
from onspace.cache import MemoryCache
from onspace.circuit_breaker import CircuitBreaker
from onspace.fallback import FallbackRouter
from onspace.providers import MockProvider
from onspace.service import OnSpaceAIService


def _service(providers=None):
    router = FallbackRouter(providers or [MockProvider()], CircuitBreaker())
    return OnSpaceAIService(router=router, cache=MemoryCache(default_ttl=60))


@pytest_asyncio.fixture
async def client():
    app = create_onspace_app(_service(), with_metrics=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/ai/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "onspace" in body["app"].lower()


@pytest.mark.asyncio
async def test_generate_endpoint_success(client):
    r = await client.post("/api/v1/ai/generate", json={"prompt": "Explain tokens"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["cached"] is False
    assert body["provider"] == "mock"
    assert "x-request-id" in r.headers


@pytest.mark.asyncio
async def test_generate_endpoint_cache_hit(client):
    payload = {"prompt": "cache me please", "model": "gpt-4o", "cache": True}
    r1 = await client.post("/api/v1/ai/generate", json=payload)
    r2 = await client.post("/api/v1/ai/generate", json=payload)
    assert r1.status_code == 200
    assert r2.json()["cached"] is True


@pytest.mark.asyncio
async def test_metrics_exposed(client):
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "onspaceai_" in r.text


@pytest.mark.asyncio
async def test_payload_too_large_returns_413(client):
    r = await client.post(
        "/api/v1/ai/generate", json={"prompt": "x" * 200000, "model": "mini"}
    )
    assert r.status_code == 413


@pytest.mark.asyncio
async def test_degraded_returns_503():
    app = create_onspace_app(_service([MockProvider(fail_status=503)]), with_metrics=False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/api/v1/ai/generate", json={"prompt": "x"})
    assert r.status_code == 503


@pytest.mark.asyncio
async def test_route_has_no_business_logic_beyond_mapping():
    """The route must delegate: swapping the service changes the response."""
    app = create_onspace_app(_service(), with_metrics=False)
    set_onspace_service(_service([MockProvider(fail_status=503)]))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/api/v1/ai/generate", json={"prompt": "cache-free", "cache": False})
    assert r.status_code == 503
