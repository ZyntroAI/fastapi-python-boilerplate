"""AgentTask — the structured hand-off between Planner and Executor.

An agent task is structured data, never a free-form string: the action is a
closed set, so an unsupported action fails validation at the boundary rather
than deep inside a provider call.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Actions that operate on a specific instance and therefore require instance_id.
INSTANCE_ACTIONS = frozenset({"start_instance", "stop_instance", "reboot_instance"})

Action = Literal[
    "list_instances",
    "start_instance",
    "stop_instance",
    "reboot_instance",
]


class AgentTask(BaseModel):
    task_id: str = Field(min_length=1)
    action: Action
    instance_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _instance_id_required_for_instance_actions(self) -> AgentTask:
        if self.action in INSTANCE_ACTIONS and not self.instance_id:
            raise ValueError(f"action {self.action!r} requires instance_id")
        return self
