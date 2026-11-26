from typing import Any, Dict from app.hooks.base import BaseHook

class TaskCreatedHook(BaseHook): name = "task-created"

async def execute(self, payload: Dict[str, Any]) -> None:
    print(f"[HOOK] Task Created => {payload}")
