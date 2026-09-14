"""Tests — ไม่ต้องใช้ Redis/FireCrawl/API จริง (mock + fail-open path)

ครอบคลุม: health, scrape fail-open (ไม่มี key), crawl async → task_id,
task status 404, webhook HMAC sign/verify.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------- health ----------
@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "FireCrawl" in body["app"]


# ---------- scrape (fail-open: ไม่มี key → คืน degraded ไม่ crash) ----------
@pytest.mark.asyncio
async def test_scrape_fail_open_no_key(client):
    """ไม่มี FIRECRAWL_API_KEY → ยังคืน 200 พร้อม error (fail-open)"""
    r = await client.post(
        "/api/v1/firecrawl/scrape",
        json={"url": "https://example.com"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert body["error"]  # มีข้อความบอกว่าไม่ได้ตั้งค่า


@pytest.mark.asyncio
async def test_scrape_invalid_url(client):
    """URL ไม่ valid → 422 จาก Pydantic"""
    r = await client.post("/api/v1/firecrawl/scrape", json={"url": "not-a-url"})
    assert r.status_code == 422


# ---------- crawl (async task → task_id) ----------
@pytest.mark.asyncio
async def test_crawl_returns_task_id(client):
    r = await client.post(
        "/api/v1/firecrawl/crawl",
        json={"url": "https://example.com", "max_pages": 5},
    )
    assert r.status_code == 202
    body = r.json()
    assert body["task_id"]
    assert body["status"] == "queued"


# ---------- task status ----------
@pytest.mark.asyncio
async def test_task_status_not_found(client):
    r = await client.get("/api/v1/firecrawl/tasks/nonexistent-id")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "not_found"


# ---------- webhook HMAC ----------
def test_webhook_sign_verify():
    from app.services.webhook import sign_payload, verify_signature

    payload = {"task_id": "abc", "data": [{"url": "https://example.com"}]}
    secret = "s3cr3t"
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, secret, sig) is True
    # ผิด secret → ไม่ผ่าน
    assert verify_signature(payload, "wrong-secret", sig) is False
    # เปลี่ยน payload → ไม่ผ่าน
    tampered = {**payload, "data": []}
    assert verify_signature(tampered, secret, sig) is False
