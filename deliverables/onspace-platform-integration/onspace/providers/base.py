"""Provider contract + error model."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

RETRYABLE_STATUS = {408, 429, 502, 503, 504}
NON_RETRYABLE_STATUS = {400, 401, 403, 422}


@dataclass
class ProviderError(Exception):
    """Provider failure carrying the HTTP status that explains it."""

    status: int = 500
    message: str = "provider error"
    retryable: bool = False

    def __post_init__(self) -> None:
        if self.status in RETRYABLE_STATUS:
            self.retryable = True
        elif self.status in NON_RETRYABLE_STATUS:
            self.retryable = False

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.status}] {self.message}"


@dataclass
class ProviderResult:
    content: str
    model: str
    tokens_used: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)


class BaseProvider(abc.ABC):
    """Every provider implements `complete`; raise ProviderError on failure."""

    name: str = "base"

    @abc.abstractmethod
    async def complete(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> ProviderResult:
        raise NotImplementedError

    async def aclose(self) -> None:
        """Optional cleanup hook for providers holding a client."""
        return None
