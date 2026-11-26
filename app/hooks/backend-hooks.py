from typing import Any, Dict from app.hooks.base import BaseHook

class BackendGenerateHook(BaseHook): name = "backend-generate"

async def execute(self, payload: Dict[str, Any]) -> None:
    print(f"[HOOK] Backend Generation => {payload}")
