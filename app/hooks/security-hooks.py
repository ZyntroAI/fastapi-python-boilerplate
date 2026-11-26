from typing import Any, Dict from app.hooks.base import BaseHook

class SecurityAlertHook(BaseHook): name = "security-alert"

async def execute(self, payload: Dict[str, Any]) -> None:
    print(f"[HOOK] Security Alert => {payload}")
