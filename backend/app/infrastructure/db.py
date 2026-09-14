"""Database infrastructure: async SQLModel engine, session factory, init.

Faithful to the merged spec — asyncpg engine driven by `database_url`, with an
`init_db()` that creates tables and a `get_session()` async generator used by
FastAPI dependencies.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables on startup (dev convenience; use Alembic in prod)."""
    # Import models so their metadata registers before create_all.
    from app.api.v1 import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
