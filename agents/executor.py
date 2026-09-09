from app.providers.base import ComputeProvider
from app.schemas.task import AgentTask

class AgentExecutor:

def __init__(self, provider: ComputeProvider):
    self.provider = provider

async def execute(self, task: AgentTask):

    if task.action == "list_instances":
        return await self.provider.list_instances()

    if task.action == "start_instance":
        return await self.provider.start_instance(
            task.instance_id
        )

    if task.action == "stop_instance":
        return await self.provider.stop_instance(
            task.instance_id
        )

    if task.action == "reboot_instance":
        return await self.provider.reboot_instance(
            task.instance_id
        )

    raise ValueError(
        f"Unsupported action: {task.action}"
    )
Flow:

Planner
↓
AgentTask
↓
Executor
↓
ComputeProvider
↓
BytePlusECSProvider
↓
BytePlus ECS
