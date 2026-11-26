import logging
from collections import defaultdict
from typing import Any, Dict, List
from app.hooks.base import BaseHook
from app.hooks.events import HookEvent

logger = logging.getLogger(__name__)


class HookRegistry:
    def __init__(self) -> None:
        self._hooks: Dict[str, List[BaseHook]] = defaultdict(list)

    def register(self, event: HookEvent | str, hook: BaseHook) -> None:
        """Register a hook for an event"""
        event_key = str(event)
        self._hooks[event_key].append(hook)
        logger.debug(f"Registered hook '{hook.name}' for event: {event_key}")

    def unregister(self, event: HookEvent | str, hook: BaseHook) -> None:
        """Unregister a hook"""
        event_key = str(event)
        if hook in self._hooks[event_key]:
            self._hooks[event_key].remove(hook)
            logger.debug(f"Unregistered hook '{hook.name}' from {event_key}")

    async def dispatch(
        self, event: HookEvent | str, payload: Dict[str, Any]
    ) -> None:
        """Dispatch event to all registered hooks"""
        event_key = str(event)
        hooks = self._hooks.get(event_key, [])

        if not hooks:
            logger.debug(f"No hooks registered for: {event_key}")
            return

        logger.debug(f"Dispatching {event_key} → {len(hooks)} hook(s)")

        for hook in hooks:
            try:
                logger.debug(f"Running: {hook.name}")
                await hook.execute(payload)
            except Exception as e:
                logger.exception(f"Hook '{hook.name}' failed: {e}")

    async def dispatch_parallel(
        self, event: HookEvent | str, payload: Dict[str, Any]
    ) -> None:
        """Run all hooks concurrently (new!)"""
        import asyncio

        event_key = str(event)
        hooks = self._hooks.get(event_key, [])

        if not hooks:
            return

        tasks = [hook.execute(payload) for hook in hooks]
        await asyncio.gather(*tasks, return_exceptions=True)


# Global singleton
registry = HookRegistry()
