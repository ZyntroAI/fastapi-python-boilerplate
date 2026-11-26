from typing import Any, Dict
from app.hooks.base import BaseHook


class TaskCreatedHook(BaseHook):
    name = "task-created"

    async def execute(self, payload: Dict[str, Any]) -> None:
        print(f"✅ [Task Hook] Created → {payload.get('id')}: {payload.get('title')}")

