import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_me_unauthenticated():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/me")
        assert r.status_code in (401, 403)

@pytest.mark.anyio
async def test_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/profile/123")
        assert r.status_code == 200
        assert r.json()["user_id"] == "123"
