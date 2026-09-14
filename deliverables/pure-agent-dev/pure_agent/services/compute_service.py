"""ComputeService — the application/business layer.

Orchestration only: plan a task, hand it to the executor. Authorisation,
quotas, audit logging and retry policy belong here, not in the route and not in
the agent.
"""

from __future__ import annotations

from pure_agent.agents.executor import AgentExecutor
from pure_agent.agents.planner import AgentPlanner
from pure_agent.schemas.compute import InstanceResponse


class ComputeService:
    def __init__(self, planner: AgentPlanner, executor: AgentExecutor) -> None:
        self.planner = planner
        self.executor = executor

    async def execute(
        self, action: str, instance_id: str | None = None
    ) -> list[InstanceResponse] | InstanceResponse:
        task = self.planner.plan(action=action, instance_id=instance_id)
        return await self.executor.execute(task)
