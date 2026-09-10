"""Tests for HTTP layer, configuration, and the Supabase task store."""
from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

import agent_core
from agent_core import AgentClient, TaskStore, get_settings
from agent_core.api import app, get_client


class StubClient(agent_core.TargetClient):
    def __init__(self, states=("completed",), result=None):
        self._states = list(states)
        self._result = result

    async def submit(self, payload):
        return "t-1"

    async def status(self, task_id):
        return self._states.pop(0) if len(self._states) > 1 else self._states[0]

    async def result(self, task_id):
        return self._result


def _wire(client):
    async def _dep():
        yield client

    app.dependency_overrides[get_client] = _dep
    return TestClient(app)


def test_import_needs_no_credentials():
    """The whole point of lazy settings: importing never requires a key."""
    assert agent_core.__version__ == "1.0.0"
    assert agent_core.AgentClient is AgentClient


def test_health():
    with TestClient(app) as tc:
        body = tc.get("/health").json()
    assert body["ok"] is True
    assert body["version"] == "1.0.0"


def test_submit_endpoint():
    tc = _wire(StubClient())
    try:
        resp = tc.post("/api/agent/submit", json={"prompt": "hello"})
        assert resp.status_code == 200
        assert resp.json()["task_id"] == "t-1"
    finally:
        app.dependency_overrides.clear()


def test_submit_rejects_empty_prompt():
    tc = _wire(StubClient())
    try:
        assert tc.post("/api/agent/submit", json={"prompt": ""}).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_status_endpoint():
    tc = _wire(StubClient(states=("running",)))
    try:
        assert tc.get("/api/agent/status/t-1").json() == {
            "task_id": "t-1",
            "status": "running",
            "result": None,
        }
    finally:
        app.dependency_overrides.clear()


def test_result_endpoint_returns_terminal_payload():
    tc = _wire(StubClient(states=("completed",), result={"out": "done"}))
    try:
        body = tc.get("/api/agent/result/t-1").json()
        assert body["status"] == "completed"
        assert body["result"] == {"out": "done"}
    finally:
        app.dependency_overrides.clear()


def test_upstream_auth_error_becomes_502():
    class AuthFailing(agent_core.TargetClient):
        async def submit(self, payload):
            raise agent_core.AgentAuthError("bad key")

        async def status(self, task_id):
            return "pending"

        async def result(self, task_id):
            return None

    tc = _wire(AuthFailing())
    try:
        resp = tc.post("/api/agent/submit", json={"prompt": "x"})
        assert resp.status_code == 502
    finally:
        app.dependency_overrides.clear()


def test_settings_require_api_key_is_loud(monkeypatch):
    monkeypatch.setenv("AGENT_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(agent_core.AgentConfigError):
        get_settings().require_api_key()
    get_settings.cache_clear()


def test_settings_lazy_defaults():
    get_settings.cache_clear()
    s = get_settings()
    assert s.AGENT_PROVIDER == "agent"
    assert s.AGENT_MAX_RETRIES == 3
    get_settings.cache_clear()


async def test_task_store_save_and_get():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        if request.method == "POST":
            return httpx.Response(201, json=[{"agent_task_id": "t-1", "status": "pending"}])
        return httpx.Response(200, json=[{"agent_task_id": "t-1", "status": "done"}])

    transport = httpx.MockTransport(handler)
    store = TaskStore(
        "https://proj.supabase.co", "svc-key",
        client=httpx.AsyncClient(transport=transport),
    )

    saved = await store.save({"agent_task_id": "t-1", "prompt": "hi"})
    assert saved["agent_task_id"] == "t-1"
    assert "/rest/v1/agent_tasks" in seen["url"]

    got = await store.get("t-1")
    assert got["status"] == "done"


async def test_task_store_requires_config(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(agent_core.AgentConfigError):
        TaskStore()
    get_settings.cache_clear()


async def test_task_store_surfaces_upstream_error():
    def handler(request):
        return httpx.Response(400, text="bad request")

    store = TaskStore(
        "https://proj.supabase.co", "svc-key",
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(agent_core.AgentAPIError):
        await store.get("t-1")
