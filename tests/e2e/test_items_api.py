"""End-to-end CRUD through Traefik — full stack validation"""
import os
import pytest
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:80")

@pytest.fixture
def client():
    return httpx.Client(base_url=API_BASE, timeout=15)

@pytest.mark.e2e
def test_create_and_fetch_item(client):
    """✅ Create item → verify stored → read back — through Traefik"""
    # Create
    create = client.post("/api/items", json={
        "title": "E2E Test Item",
        "description": "Created via Traefik ingress"
    })
    assert create.status_code in (200, 201)
    item = create.json()
    assert item["title"] == "E2E Test Item"
    item_id = item["id"]

    # Fetch via Traefik
    fetch = client.get(f"/api/items/{item_id}")
    assert fetch.status_code == 200
    fetched = fetch.json()
    assert fetched["id"] == item_id
    assert fetched["title"] == "E2E Test Item"

@pytest.mark.e2e
def test_list_items_through_traefik(client):
    """✅ Item list endpoint accessible through Traefik"""
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
