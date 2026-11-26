from typing import Any, Dict
from app.hooks.events import HookEvent
from app.hooks.registry import registry


class HookService:
    @staticmethod
    async def emit(event: HookEvent | str, payload: Dict[str, Any]) -> None:
        """Emit an event → sequential execution"""
        await registry.dispatch(event, payload)

    @staticmethod
    async def emit_parallel(event: HookEvent | str, payload: Dict[str, Any]) -> None:
        """Emit an event → all hooks run at once"""
        await registry.dispatch_parallel(event, payload)
