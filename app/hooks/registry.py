from collections import defaultdict from typing import Dict, List from app.hooks.base import BaseHook

class HookRegistry: def init(self): self._hooks: Dict[str, List[BaseHook]] = defaultdict(list)

def register(self, event: str, hook: BaseHook) -> None:
    self._hooks[event].append(hook)

async def dispatch(self, event: str, payload: dict) -> None:
    hooks = self._hooks.get(event, [])
    for hook in hooks:
        await hook.execute(payload)
registry = HookRegistry()  
