import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_search_items():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search?q=fastapi")
    assert response.status_code == 200
    assert "fastapi" in str(response.json()).lower()
