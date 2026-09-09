"""Integration tests for the Item CRUD API + health + JWT auth."""
from __future__ import annotations

import pytest

from app.core.security import create_access_token


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_crud_roundtrip(client):
    # create
    r = await client.post("/api/v1/items", json={"name": "first", "description": "hello"})
    assert r.status_code == 201
    body = r.json()
    item_id = body["id"]
    assert body["name"] == "first"

    # list
    r = await client.get("/api/v1/items")
    assert r.status_code == 200
    assert any(i["id"] == item_id for i in r.json())

    # get one
    r = await client.get(f"/api/v1/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["description"] == "hello"

    # update
    r = await client.patch(f"/api/v1/items/{item_id}", json={"name": "renamed"})
    assert r.status_code == 200
    assert r.json()["name"] == "renamed"

    # delete
    r = await client.delete(f"/api/v1/items/{item_id}")
    assert r.status_code == 204

    # gone -> 404
    r = await client.get(f"/api/v1/items/{item_id}")
    assert r.status_code == 404


async def test_create_duplicate_conflict(client):
    await client.post("/api/v1/items", json={"name": "dup"})
    r = await client.post("/api/v1/items", json={"name": "dup"})
    assert r.status_code == 409
    assert r.json()["code"] == "conflict"


async def test_missing_item_404(client):
    r = await client.get("/api/v1/items/9999")
    assert r.status_code == 404


async def test_protected_route_requires_token(client):
    r = await client.get("/api/v1/items/me")
    assert r.status_code == 401

    token = create_access_token("alice")
    r = await client.get("/api/v1/items/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


async def test_validation_error_422(client):
    r = await client.post("/api/v1/items", json={"name": ""})
    assert r.status_code == 422
