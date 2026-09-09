from app.schemas.task import AgentTask

class AgentPlanner:

def plan(
    self,
    action: str,
    instance_id: str | None = None,
) -> AgentTask:
    return AgentTask(
        task_id="generated-task",
        action=action,
        instance_id=instance_id,
    )
Planner ไม่ควรเรียก BytePlus.

User intent
↓
Planner
↓
AgentTask

ไม่ใช่:

User intent
↓
Planner
↓
BytePlus API
