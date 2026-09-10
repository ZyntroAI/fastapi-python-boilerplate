"""Planner — intent in, structured AgentTask out.

The Planner never calls a provider, and never will: it converts a request into
a task and stops. Keeping it provider-free is what makes it unit-testable with
no mocks beyond a task_id generator.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from pure_agent.schemas.task import AgentTask


class AgentPlanner:
    def __init__(self, task_id_factory: Callable[[], str] | None = None) -> None:
        # Injectable so tests can assert on a stable id.
        self._new_task_id = task_id_factory or (lambda: str(uuid.uuid4()))

    def plan(self, action: str, instance_id: str | None = None) -> AgentTask:
        return AgentTask(
            task_id=self._new_task_id(),
            action=action,  # type: ignore[arg-type]  # validated by AgentTask
            instance_id=instance_id,
        )
