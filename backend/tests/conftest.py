"""Test fixtures — in-memory SQLite (aiosqlite) so tests need no PostgreSQL.

Environment is set to `production` so the app lifespan skips auto-creating
tables on the (unused) asyncpg engine; we then create tables on a fresh
aiosqlite engine and override the `get_db` dependency with it.
"""
from __future__ import annotations

import os

os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from app.api import deps  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[deps.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()
