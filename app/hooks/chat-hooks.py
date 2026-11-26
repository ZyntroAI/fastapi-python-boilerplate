from typing import Any, Dict from app.hooks.base import BaseHook

class ChatSummaryHook(BaseHook): name = "chat-summary"

async def execute(self, payload: Dict[str, Any]) -> None:
    print(f"[HOOK] Chat Summarized => {payload}")
