"""End-to-end tests — hit API through Traefik ingress"""
import os
import pytest
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:80")

@pytest.mark.e2e
def test_health_endpoint_through_traefik():
    """✅ Health check works via Traefik routing"""
    resp = httpx.get(f"{API_BASE}/health", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("healthy", "ok")

@pytest.mark.e2e
def test_api_swagger_ui_available():
    """✅ Swagger docs accessible via Traefik"""
    resp = httpx.get(f"{API_BASE}/docs", timeout=10)
    assert resp.status_code == 200
    assert "swagger" in resp.text.lower()
