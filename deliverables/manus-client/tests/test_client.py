"""Tests — ใช้ mock ไม่ต้องใช้ API key จริง / ไม่ต้องแตะ network"""
import asyncio

import pytest

from manus_client.client import ManusClient, ManusAPIError

API_KEY = "manus_test_1234567890abcdef"


def make_client(**kw):
    return ManusClient(api_key=API_KEY, **kw)


def async_lambda(value):
    async def f(*a, **k):
        return value
    return f


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------- constructor ----------
def test_requires_auth():
    with pytest.raises(ValueError):
        ManusClient()


def test_api_key_header():
    c = make_client()
    assert c._headers["X-Manus-API-Key"] == API_KEY
    assert "Authorization" not in c._headers


def test_bearer_alternative():
    c = ManusClient(bearer_token="tok123")
    assert c._headers["Authorization"] == "Bearer tok123"
    assert "X-Manus-API-Key" not in c._headers


# ---------- create_task success + auth header ----------
def test_create_task_success():
    c = make_client()

    captured = {}

    async def fake_request(method, path, json_body=None):
        captured["path"] = path
        captured["json"] = json_body
        return {"ok": True, "request_id": "req1", "taskId": "task_abc", "status": "pending"}

    c._request = fake_request  # type: ignore[method-assign]
    out = run(c.create_task("do something", {"response_format": "json"}))

    assert captured["path"] == "/task.create"
    assert captured["json"]["task"] == "do something"
    assert captured["json"]["options"] == {"response_format": "json"}
    assert out["taskId"] == "task_abc"


# ---------- endpoints map ไป dot-notation ----------
def test_list_messages_path():
    c = make_client()
    seen = {}

    async def fake_request(method, path, json_body=None):
        seen["path"] = path
        seen["body"] = json_body
        return {"ok": True, "request_id": "r", "data": []}

    c._request = fake_request  # type: ignore[method-assign]
    run(c.list_messages("task_1"))
    assert seen["path"] == "/task.listMessages"
    assert seen["body"] == {"taskId": "task_1"}


def test_stop_and_webhook_paths():
    c = make_client()
    seen = []

    async def fake_request(method, path, json_body=None):
        seen.append((path, json_body))
        return {"ok": True, "request_id": "r"}

    c._request = fake_request  # type: ignore[method-assign]
    run(c.stop_task("t1"))
    run(c.create_webhook("t1", "https://x.com/h"))
    assert seen[0][0] == "/task.stop"
    assert seen[1][0] == "/webhook.create"
    assert seen[1][1] == {"taskId": "t1", "url": "https://x.com/h"}


# ---------- error mapping ----------
def test_error_raises_manus_error():
    async def bad_req(method, path, json_body=None):
        raise ManusAPIError("missing authentication", code="unauthenticated", request_id="r_err")

    c = make_client()
    c._request = bad_req  # type: ignore[method-assign]
    with pytest.raises(ManusAPIError) as exc:
        run(c.create_task("x"))
    assert exc.value.code == "unauthenticated"
    assert exc.value.request_id == "r_err"


# ---------- run_task polling ----------
def test_run_task_completes():
    c = make_client()
    created = {"ok": True, "request_id": "r1", "taskId": "task_1"}
    msgs = {"ok": True, "request_id": "r2", "data": [{"status": "stopped", "content": "done"}]}
    c.create_task = async_lambda(created)  # type: ignore[method-assign]
    c.list_messages = async_lambda(msgs)  # type: ignore[method-assign]
    out = run(c.run_task("job", interval=0.01))
    assert out["data"][0]["status"] == "stopped"


def test_run_task_timeout():
    c = make_client()
    c.create_task = async_lambda({"ok": True, "request_id": "r1", "taskId": "task_1"})  # type: ignore[method-assign]
    c.list_messages = async_lambda({"ok": True, "request_id": "r2", "data": [{"status": "running"}]})  # type: ignore[method-assign]
    with pytest.raises(ManusAPIError) as exc:
        run(c.run_task("job", interval=0.01, max_wait=0.05))
    assert exc.value.code == "timeout"


def test_run_task_missing_id():
    c = make_client()
    c.create_task = async_lambda({"ok": True, "request_id": "r1"})  # type: ignore[method-assign]
    with pytest.raises(ManusAPIError) as exc:
        run(c.run_task("job"))
    assert exc.value.code == "no_task_id"
