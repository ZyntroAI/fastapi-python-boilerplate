"""Tests for polling: terminal handling, result fetching, and the timeout."""
from __future__ import annotations

import pytest

from agent_core import AgentPollTimeoutError, TargetClient, poll_task


class FakeClient(TargetClient):
    """Scripted provider: each status() call pops the next state."""

    def __init__(self, states, result=None, error=None):
        self._states = list(states)
        self._result = result
        self._error = error
        self.status_calls = 0
        self.result_calls = 0

    async def submit(self, payload):
        return "t-1"

    async def status(self, task_id):
        self.status_calls += 1
        if self._error:
            raise self._error
        if len(self._states) > 1:
            return self._states.pop(0)
        return self._states[0]

    async def result(self, task_id):
        self.result_calls += 1
        return self._result


async def test_polls_until_completed_and_fetches_result(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr("agent_core.polling.asyncio.sleep", no_sleep)
    client = FakeClient(["pending", "running", "completed"], result={"out": 42})

    out = await poll_task("t-1", client, interval=0)

    assert out.status == "completed"
    assert out.result == {"out": 42}
    assert client.result_calls == 1


async def test_failed_task_does_not_fetch_result(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr("agent_core.polling.asyncio.sleep", no_sleep)
    client = FakeClient(["running", "failed"])

    out = await poll_task("t-1", client, interval=0)

    assert out.status == "failed"
    assert out.result is None
    assert client.result_calls == 0, "a failed task has no result to fetch"


async def test_timeout_raises_instead_of_hanging(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr("agent_core.polling.asyncio.sleep", no_sleep)

    # Clock jumps past the budget once we have polled at least twice.
    ticks = {"n": 0, "now": 0.0}

    def fake_clock() -> float:
        ticks["n"] += 1
        if ticks["n"] > 2:
            ticks["now"] = 999.0
        return ticks["now"]

    monkeypatch.setattr("agent_core.polling.time.monotonic", fake_clock)

    client = FakeClient(["running"])  # never terminal
    with pytest.raises(AgentPollTimeoutError) as exc:
        await poll_task("t-1", client, interval=0, timeout=5.0)

    assert exc.value.last_status == "running"


async def test_cancelled_is_terminal(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr("agent_core.polling.asyncio.sleep", no_sleep)
    client = FakeClient(["running", "cancelled"])

    out = await poll_task("t-1", client, interval=0)

    assert out.status == "cancelled"
