import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_user_registration():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"username": "testuser", "password": "123456"}
        response = await ac.post("/users/register", json=payload)
    assert response.status_code == 201
