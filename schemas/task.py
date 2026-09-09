from typing import Literal

from pydantic import BaseModel, Field

class AgentTask(BaseModel):
task_id: str
action: Literal[
"list_instances",
"start_instance",
"stop_instance",
"reboot_instance",
]
instance_id: str | None = Field(
default=None,
)

ตัวนี้ต้องสอดคล้องกับ:

schemas/agent-task.schema.json

ดังนั้นจะมีสองระดับ:

JSON Schema
↓
External contract
↓
Pydantic
↓
Runtime validation
