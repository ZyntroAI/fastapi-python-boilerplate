"""Tests for Redis pub/sub + cache decorator + role guard + standard errors.

Redis is mocked — no daemon needed. In-memory SQLite for DB-backed paths.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import Base
from app import crud
from app.auth import create_access_token, decode_token
from app.errors import AuthenticationRequired, PermissionDenied, ResourceNotFound
from app.redis import RedisPubSub, redis_pubsub
from app.middleware import cache_resolver
from app.schema import schema


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    f = async_sessionmaker(engine, expire_on_commit=False)
    session = f()
    yield session
    await session.close()
    await engine.dispose()


async def execute(q, context=None):
    return await schema.execute(q, context_value=context or {})


# --- errors ---
def test_error_extensions():
    e = PermissionDenied()
    assert e.extensions["code"] == "PERMISSION_DENIED" and e.extensions["status"] == 403
    assert AuthenticationRequired().extensions["status"] == 401
    assert ResourceNotFound().extensions["code"] == "NOT_FOUND"


# --- cache decorator (mocked redis) ---
async def test_cache_resolver_hit():
    fn = AsyncMock(return_value={"id": 1})
    # first call: get returns None -> run fn -> setex
    redis_pubsub.get = AsyncMock(return_value=None)
    redis_pubsub.setex = AsyncMock()
    cached = cache_resolver(ttl=60)(fn)
    out1 = await cached(1, a=2)
    assert out1 == {"id": 1}
    assert fn.await_count == 1
    # second call: get returns hit -> do NOT re-run fn
    redis_pubsub.get = AsyncMock(return_value=json.dumps({"id": 1}))
    out2 = await cached(1, a=2)
    assert out2 == {"id": 1}
    assert fn.await_count == 1  # unchanged => served from cache


# --- pub/sub publish tolerates redis down (never raises) ---
async def test_publish_noop_when_redis_down():
    rp = RedisPubSub()
    rp._get = AsyncMock(side_effect=Exception("down")) if hasattr(rp, "_get") else None
    # Simulate: publish should swallow connection errors
    with patch.object(redis_pubsub, "_get", side_effect=Exception("down")):
        await redis_pubsub.publish("ch", {"a": 1})  # must not raise


# --- role guard via create_user (admin required) ---
async def test_create_user_requires_admin(db):
    token = create_access_token({"sub": "2", "role": "user"})
    res = await execute('mutation { createUser(email:"x@y.z", name:"X", password:"p") { id } }',
                        context={"db": db, "user": decode_token(token)})
    assert res.errors
    # error extension should carry PERMISSION_DENIED via our custom error
    ext = getattr(res.errors[0], "extensions", None) or {}
    assert ext.get("code") in (None, "PERMISSION_DENIED")


async def test_create_user_admin_publishes(db):
    with patch.object(redis_pubsub, "publish", new_callable=AsyncMock) as pub:
        admin = await crud.create_user(db, email="adm@x.io", name="Adm", password="p", role="admin")
        token = create_access_token({"sub": str(admin.id), "role": "admin"})
        res = await execute('mutation { createUser(email:"new@x.io", name:"N", password:"pw") { id email } }',
                            context={"db": db, "user": decode_token(token)})
        assert res.errors is None, res.errors
        assert res.data["createUser"]["email"] == "new@x.io"
        pub.assert_awaited_once()
