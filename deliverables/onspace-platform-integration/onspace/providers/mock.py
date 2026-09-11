"""Mock provider — deterministic, for tests and local development."""
from __future__ import annotations

from typing import Dict, List, Optional

from .base import BaseProvider, ProviderError, ProviderResult


class MockProvider(BaseProvider):
    """Echoes the last user message. Never needs an API key."""

    name = "mock"

    def __init__(self, fail_status: Optional[int] = None, echo: bool = True) -> None:
        self._fail_status = fail_status
        self._echo = echo

    async def complete(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> ProviderResult:
        if self._fail_status is not None:
            raise ProviderError(status=self._fail_status, message=f"mock fail {self._fail_status}")
        last = messages[-1]["content"] if messages else ""
        content = f"[{self.name}:{model}] {last[:max_tokens]}" if self._echo else ""
        return ProviderResult(content=content, model=model, tokens_used=10)
