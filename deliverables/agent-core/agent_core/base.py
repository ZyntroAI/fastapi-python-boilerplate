"""Provider interface contract — the seam that keeps providers swappable."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

#: Task states that mean "stop polling".
TERMINAL_STATUSES: frozenset[str] = frozenset({"completed", "failed", "cancelled"})


class TargetClient(ABC):
    """Minimal async contract every agent provider must satisfy."""

    @abstractmethod
    async def submit(self, payload: dict[str, Any]) -> str:
        """Create a task and return its provider-side id."""

    @abstractmethod
    async def status(self, task_id: str) -> str:
        """Return the current state: pending | running | completed | failed …"""

    @abstractmethod
    async def result(self, task_id: str) -> dict[str, Any] | None:
        """Return the final payload once the task is terminal, else ``None``."""

    async def aclose(self) -> None:  # pragma: no cover - trivial default
        """Release network resources. Overridable; safe to call twice."""
        return None
