"""Executor — takes an AgentTask and drives whichever provider was injected.

It depends on the ComputeProvider interface, never on a concrete adapter. That
single line is the whole architecture: swap the provider, the Executor does not
change.
"""

from __future__ import annotations

from pure_agent.providers.base import ComputeProvider
from pure_agent.schemas.compute import InstanceResponse
from pure_agent.schemas.task import AgentTask


class UnsupportedActionError(ValueError):
    """Raised for an action the executor has no handler for."""


# action -> the ComputeProvider method that serves it
_INSTANCE_HANDLERS = {
    "start_instance": "start_instance",
    "stop_instance": "stop_instance",
    "reboot_instance": "reboot_instance",
}


class AgentExecutor:
    def __init__(self, provider: ComputeProvider) -> None:
        self.provider = provider

    async def execute(self, task: AgentTask) -> list[InstanceResponse] | InstanceResponse:
        if task.action == "list_instances":
            return await self.provider.list_instances()

        handler = _INSTANCE_HANDLERS.get(task.action)
        if handler is None:
            raise UnsupportedActionError(f"Unsupported action: {task.action}")

        # Deliberately a raise, not an assert: `assert` is stripped under
        # `python -O`, which would turn this guard into a silent None passed to
        # the provider. AgentTask already enforces this; the check is the
        # executor's own, for tasks constructed without validation.
        if task.instance_id is None:
            raise UnsupportedActionError(f"action {task.action!r} requires instance_id")

        return await getattr(self.provider, handler)(task.instance_id)
