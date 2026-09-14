"""Tests for the Agent client: auth, error mapping, retry semantics."""
from __future__ import annotations

import httpx
import pytest

from agent_core import AgentClient, errors


def _client(handler, **kw):
    """Client wired to a mock transport — no network, no real sleeps."""
    transport = httpx.MockTransport(handler)
    return AgentClient(api_key="test-key", transport=transport, retries=3, **kw)


async def test_submit_returns_task_id():
    async def handler(request):
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(200, json={"task_id": "t-1"})

    async with _client(handler) as client:
        assert await client.submit({"prompt": "hi"}) == "t-1"


async def test_status_and_result():
    async def handler(request):
        if request.url.path.endswith("/result"):
            return httpx.Response(200, json={"output": "done"})
        return httpx.Response(200, json={"status": "completed"})

    async with _client(handler) as client:
        assert await client.status("t-1") == "completed"
        assert await client.result("t-1") == {"output": "done"}


async def test_result_204_is_none():
    async def handler(request):
        return httpx.Response(204)

    async with _client(handler) as client:
        assert await client.result("t-1") is None


async def test_401_maps_to_auth_error_and_is_not_retried():
    calls = {"n": 0}

    async def handler(request):
        calls["n"] += 1
        return httpx.Response(401, json={"error": "bad key"})

    async with _client(handler) as client:
        with pytest.raises(errors.AgentAuthError):
            await client.submit({"prompt": "hi"})
    assert calls["n"] == 1, "4xx must not be retried"


async def test_429_is_retried_then_succeeds(monkeypatch):
    calls = {"n": 0}
    sleeps = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr("agent_core.retry.asyncio.sleep", fake_sleep)

    async def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(429, json={"error": "slow down"})
        return httpx.Response(200, json={"task_id": "t-9"})

    async with _client(handler) as client:
        assert await client.submit({"prompt": "hi"}) == "t-9"

    assert calls["n"] == 3
    assert sleeps == [1.0, 2.0], "exponential backoff: 1s then 2s"


async def test_retry_exhaustion_reraises_original_error(monkeypatch):
    async def fake_sleep(delay):  # never actually wait
        return None

    monkeypatch.setattr("agent_core.retry.asyncio.sleep", fake_sleep)

    async def handler(request):
        return httpx.Response(500, text="boom")

    client = _client(handler)
    async with client:
        with pytest.raises(errors.AgentAPIError) as exc:
            await client.submit({"prompt": "hi"})

    # The real error survives — not swallowed behind a generic RuntimeError.
    assert exc.value.status == 500
    assert "boom" in exc.value.detail


async def test_missing_api_key_raises_config_error(monkeypatch):
    monkeypatch.setenv("AGENT_API_KEY", "")
    from agent_core import get_settings

    get_settings.cache_clear()

    async def handler(request):  # pragma: no cover - never reached
        return httpx.Response(200, json={"task_id": "x"})

    client = AgentClient(api_key="", transport=httpx.MockTransport(handler))
    async with client:
        with pytest.raises(errors.AgentAuthError):
            await client.submit({"prompt": "hi"})
    get_settings.cache_clear()


async def test_timeout_maps_to_agent_timeout_error(monkeypatch):
    async def fake_sleep(delay):
        return None

    monkeypatch.setattr("agent_core.retry.asyncio.sleep", fake_sleep)

    async def handler(request):
        raise httpx.ConnectTimeout("too slow")

    client = _client(handler)
    async with client:
        with pytest.raises(errors.AgentTimeoutError):
            await client.submit({"prompt": "hi"})


async def test_submit_without_task_id_raises_api_error():
    async def handler(request):
        return httpx.Response(200, json={"unexpected": True})

    async with _client(handler) as client:
        with pytest.raises(errors.AgentAPIError):
            await client.submit({"prompt": "hi"})
