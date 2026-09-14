"""End-to-end DB-backed resolver tests — create user, login, me, users list."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import Base
from app import crud
from app.auth import create_access_token, decode_token
from app.schema import schema


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    session = factory()
    yield session
    await session.close()
    await engine.dispose()


async def execute(q, context=None):
    return await schema.execute(q, context_value=context or {})


async def test_create_and_login_and_me_roundtrip(db):
    # admin creates a user (real insert)
    await crud.create_user(db, email="admin@x.io", name="Admin", password="pw", role="admin")
    await crud.create_user(db, email="u@x.io", name="U", password="secret", role="user")

    # login as user -> real token
    res = await execute('mutation { login(email:"u@x.io", password:"secret") { accessToken user { id email } } }',
                        context={"db": db, "user": None})
    assert res.errors is None, res.errors
    token = res.data["login"]["accessToken"]
    assert res.data["login"]["user"]["email"] == "u@x.io"

    # me with real token -> returns DB row
    payload = decode_token(token)
    me = await execute("{ me { id email role } }", context={"db": db, "user": payload})
    assert me.errors is None, me.errors
    assert me.data["me"]["email"] == "u@x.io"

    # bad password rejected
    bad = await execute('mutation { login(email:"u@x.io", password:"wrong") { accessToken } }',
                        context={"db": db, "user": None})
    assert bad.errors  # invalid creds


async def test_users_pagination_from_db(db):
    await crud.create_user(db, email="a@x.io", name="A", password="p", role="admin")
    await crud.create_user(db, email="b@x.io", name="B", password="p", role="user")
    await crud.create_user(db, email="c@x.io", name="C", password="p", role="user")
    admin_token = create_access_token({"sub": "1", "role": "admin"})
    res = await execute("{ users(first:2) { edges { node { email } } totalCount } }",
                        context={"db": db, "user": decode_token(admin_token)})
    assert res.errors is None, res.errors
    assert res.data["users"]["totalCount"] == 3
    assert len(res.data["users"]["edges"]) == 2


async def test_create_user_requires_admin(db):
    token = create_access_token({"sub": "2", "role": "user"})
    res = await execute('mutation { createUser(email:"x@y.z", name:"X", password:"p") { id } }',
                        context={"db": db, "user": decode_token(token)})
    assert res.errors  # permission denied
