# tests/conftest.py
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.routes import get_current_user

fake_user = {"id": 1, "email": "test@example.com", "role": "user"}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()
