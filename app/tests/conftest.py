# tests/conftest.py
import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.config import Settings
from app.db.session import get_session as app_get_session

@pytest.fixture(scope="session")
def event_loop():
    # speeds up async tests
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def settings():
    s = Settings()
    return s

@pytest.fixture(scope="session")
def engine(settings):
    # Use a dedicated test DB url in .env, e.g. DATABASE_URL_TEST
    # If you don’t have it yet, reuse DATABASE_URL with a test DB schema.
    db_url = getattr(settings, "DATABASE_URL_TEST", None) or settings.DATABASE_URL
    return create_async_engine(db_url, pool_pre_ping=True, future=True)

@pytest.fixture
async def db_session(engine):
    # Each test runs in its own transaction for isolation
    async with engine.connect() as conn:
        trans = await conn.begin()
        SessionTest = sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        async with SessionTest() as session:
            yield session
        await trans.rollback()

@pytest.fixture
def app(db_session):
    app_ = create_app()

    # Override the session dependency so routes use our test session
    async def override_get_session():
        yield db_session

    app_.dependency_overrides[app_get_session.__module__ + ".get_session"] = override_get_session
    # better: directly override by importing the dependency object; see below note

    # NOTE: if override line fails in your codebase, do this instead:
    # from app.db.session import get_session
    # app_.dependency_overrides[get_session] = override_get_session

    return app_

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
