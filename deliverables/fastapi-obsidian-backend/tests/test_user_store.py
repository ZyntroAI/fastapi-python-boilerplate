"""Tests for the JWT secret validation and the DB-backed user store."""
import os
import secrets
import uuid

import pytest

# Configure before importing the app modules.
TEST_DB = f"/tmp/fastapi_obsidian_users_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from app.security import _validate_secret  # noqa: E402
from app.user_store import UserStore  # noqa: E402


@pytest.fixture(scope="module")
def store():
    s = UserStore()
    s.init()
    yield s
    from app.user_store import engine
    engine.dispose()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# --- JWT secret validation ---

def test_strong_secret_accepted():
    good = secrets.token_urlsafe(48)
    assert _validate_secret(good) == good


def test_short_secret_rejected():
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        _validate_secret("tooshort")


def test_placeholder_secret_rejected():
    with pytest.raises(RuntimeError, match="insecure placeholder"):
        _validate_secret("replace-me-with-a-48-byte-random-secret")


# --- User store ---

def test_create_and_get(store):
    username = f"alice_{uuid.uuid4().hex[:8]}"
    store.create(username, "hashed-value", allowed_skills=None)
    record = store.get(username)
    assert record is not None
    assert record["username"] == username
    assert record["hashed_password"] == "hashed-value"
    assert record["allowed_skills"] is None


def test_missing_user_returns_none(store):
    assert store.get("nobody-here") is None


def test_exists(store):
    username = f"bob_{uuid.uuid4().hex[:8]}"
    assert store.exists(username) is False
    store.create(username, "h")
    assert store.exists(username) is True


def test_unrestricted_by_default(store):
    username = f"carol_{uuid.uuid4().hex[:8]}"
    store.create(username, "h")
    assert store.allowed_skills(username) is None


def test_restricted_user_returns_set(store):
    username = f"erin_{uuid.uuid4().hex[:8]}"
    store.create(username, "h", allowed_skills=["research"])
    assert store.allowed_skills(username) == {"research"}


def test_set_allowed_skills(store):
    username = f"frank_{uuid.uuid4().hex[:8]}"
    store.create(username, "h")
    assert store.set_allowed_skills(username, ["deck"]) is True
    assert store.allowed_skills(username) == {"deck"}
    assert store.set_allowed_skills("ghost", ["x"]) is False


def test_persistence_across_store_instances(store):
    """A fresh store instance reads the same rows — proves it is on disk."""
    username = f"grace_{uuid.uuid4().hex[:8]}"
    store.create(username, "h", allowed_skills=["research"])
    fresh = UserStore()
    fresh.init()
    record = fresh.get(username)
    assert record is not None
    assert record["allowed_skills"] == ["research"]
