from abc import ABC, abstractmethod from typing import Any, Dict

class BaseHook(ABC): name: str

@abstractmethod
async def execute(self, payload: Dict[str, Any]) -> None:
    pass
