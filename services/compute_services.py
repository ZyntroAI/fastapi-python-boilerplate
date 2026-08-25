def __init__(
    self,
    planner: AgentPlanner,
    executor: AgentExecutor,
):
    self.planner = planner
    self.executor = executor

async def execute(
    self,
    action: str,
    instance_id: str | None = None,
):
    task = self.planner.plan(
        action=action,
        instance_id=instance_id,
    )

    return await self.executor.execute(task)
