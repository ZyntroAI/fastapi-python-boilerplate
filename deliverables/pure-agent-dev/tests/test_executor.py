"""Executor: AgentTask -> provider, always through the interface."""

from __future__ import annotations

import pytest

from pure_agent.agents.executor import AgentExecutor, UnsupportedActionError
from pure_agent.schemas.task import AgentTask


async def test_execute_routes_each_action(mock_provider):
    ex = AgentExecutor(mock_provider)

    listed = await ex.execute(AgentTask(task_id="t", action="list_instances"))
    assert [i.instance_id for i in listed] == ["i-test-001", "i-test-002"]

    started = await ex.execute(
        AgentTask(task_id="t", action="start_instance", instance_id="i-test-001")
    )
    assert started.status == "starting"

    stopped = await ex.execute(
        AgentTask(task_id="t", action="stop_instance", instance_id="i-test-001")
    )
    assert stopped.status == "stopping"

    rebooted = await ex.execute(
        AgentTask(task_id="t", action="reboot_instance", instance_id="i-test-001")
    )
    assert rebooted.status == "rebooting"


async def test_executor_uses_whatever_provider_it_is_given(mock_provider):
    """Swap the provider, the executor is unchanged — the point of the interface."""
    calls = []

    class Recording:
        async def list_instances(self):
            calls.append("list")
            return []

        async def start_instance(self, instance_id):
            calls.append(("start", instance_id))
            return None

        async def stop_instance(self, instance_id):
            calls.append(("stop", instance_id))
            return None

        async def reboot_instance(self, instance_id):
            calls.append(("reboot", instance_id))
            return None

    ex = AgentExecutor(Recording())  # type: ignore[arg-type]
    await ex.execute(AgentTask(task_id="t", action="list_instances"))
    await ex.execute(AgentTask(task_id="t", action="start_instance", instance_id="i-9"))
    assert calls == ["list", ("start", "i-9")]


async def test_unsupported_action_raises(mock_provider):
    ex = AgentExecutor(mock_provider)
    task = AgentTask(task_id="t", action="list_instances").model_copy(
        update={"action": "nonsense"}
    )
    with pytest.raises(UnsupportedActionError):
        await ex.execute(task)


async def test_executor_depends_only_on_the_interface(mock_provider):
    import inspect

    from pure_agent.agents import executor as executor_module

    source = inspect.getsource(executor_module)
    assert "from pure_agent.providers.base import ComputeProvider" in source
    assert "byteplus" not in source.lower()
    assert "mock" not in source.lower()
