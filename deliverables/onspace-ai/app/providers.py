"""Provider abstraction — contract + error model + retryable status"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

RETRYABLE_STATUS = {408, 429, 502, 503, 504}
NON_RETRYABLE_STATUS = {400, 401, 403, 422}


@dataclass
class ProviderError(Exception):
    """Error จาก provider พร้อมสถานะ HTTP ที่จำลอง"""

    status: int = 500
    message: str = "provider error"
    retryable: bool = False

    def __post_init__(self) -> None:
        if self.status in RETRYABLE_STATUS:
            self.retryable = True


@dataclass
class ProviderResult:
    content: str
    model: str
    tokens_used: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)


class BaseProvider(abc.ABC):
    """Contract ของ provider ทุกตัว"""

    name: str = "base"

    @abc.abstractmethod
    async def complete(self, system: str, messages: List[Dict], model: str, max_tokens: int) -> ProviderResult:
        """เรียก LLM — ต้อง raise ProviderError เมื่อ fail"""
        raise NotImplementedError


class MockProvider(BaseProvider):
    """Provider จำลองสำหรับทดสอบ/local — ใช้เมื่อไม่มี key"""

    name = "mock"

    def __init__(self, fail_status: Optional[int] = None, echo: bool = True) -> None:
        self._fail_status = fail_status
        self._echo = echo

    async def complete(self, system: str, messages: List[Dict], model: str, max_tokens: int) -> ProviderResult:
        if self._fail_status is not None:
            raise ProviderError(status=self._fail_status, message=f"mock fail {self._fail_status}")
        last = messages[-1]["content"] if messages else ""
        content = f"[{self.name}:{model}] {last[:max_tokens]}" if self._echo else ""
        return ProviderResult(content=content, model=model, tokens_used=10)


class OpenAIProvider(BaseProvider):
    """OpenAI — lazy import SDK เพื่อให้ import module ไม่พึ่ง key"""

    name = "openai"

    async def complete(self, system: str, messages: List[Dict], model: str, max_tokens: int) -> ProviderResult:
        from app.config import get_settings

        key = get_settings().openai_api_key
        if not key:
            raise ProviderError(status=401, message="OPENAI_API_KEY not set")
        # TODO: ต่อ OpenAI SDK จริง — คง interface ไว้ให้ใช้งาน production
        raise ProviderError(status=501, message="OpenAI provider not wired (mock only in this build)")
