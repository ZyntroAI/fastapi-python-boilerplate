"""Tests: FastAPI endpoints (health + /api/ai + cache + degraded)"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "onspace" in body["app"].lower()


@pytest.mark.asyncio
async def test_ai_endpoint_success(client):
    r = await client.post("/api/ai", json={"prompt": "Explain tokens", "model": "gpt-4o"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["cached"] is False
    assert "content" in body
    assert "x-request-id" in r.headers


@pytest.mark.asyncio
async def test_ai_endpoint_cache_hit(client):
    # เรียกซ้ำ prompt เดียว → cache hit
    payload = {"prompt": "cache me please", "model": "gpt-4o", "cache": True}
    r1 = await client.post("/api/ai", json=payload)
    assert r1.status_code == 200
    r2 = await client.post("/api/ai", json=payload)
    assert r2.status_code == 200
    assert r2.json()["cached"] is True


@pytest.mark.asyncio
async def test_metrics_exposed(client):
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "onspaceai_" in r.text


@pytest.mark.asyncio
async def test_auth_required_when_key_set(client, monkeypatch):
    from app.config import get_settings

    s = get_settings()
    monkeypatch.setattr(s, "api_key", "secret123")
    # ไม่มี key → 401
    r = await client.post("/api/ai", json={"prompt": "x"})
    assert r.status_code == 401
    # มี key ถูก → ผ่าน
    r2 = await client.post("/api/ai", json={"prompt": "x"}, headers={"x-api-key": "secret123"})
    assert r2.status_code == 200
    monkeypatch.setattr(s, "api_key", "")


@pytest.mark.asyncio
async def test_payload_too_large(client):
    # model mini มี budget 32k — ส่ง payload ใหญ่เกิน
    big = "x" * 200000
    r = await client.post("/api/ai", json={"prompt": big, "model": "mini"})
    assert r.status_code == 413
