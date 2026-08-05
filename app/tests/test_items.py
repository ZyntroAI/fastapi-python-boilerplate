# tests/test_items.py
import pytest

pytestmark = pytest.mark.anyio

async def auth_header_for_token(token: str):
    # if you have a real JWT generator, use that fixture instead
    return {"Authorization": f"Bearer {token}"}

async def test_create_item_ok(client):
    # You may need to mock get_current_user or provide a valid JWT fixture.
    resp = await client.post(
        "/items",
        json={"name": "foo"},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "id" in data
    assert data["name"] == "foo"

async def test_list_items_pagination(client):
    resp = await client.get(
        "/items?limit=5&offset=0",
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 5
