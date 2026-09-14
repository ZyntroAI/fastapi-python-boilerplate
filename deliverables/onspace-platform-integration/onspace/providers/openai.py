"""OpenAI provider — lazy SDK import so a missing key never breaks import."""
from __future__ import annotations

from typing import Dict, List

from .base import BaseProvider, ProviderError, ProviderResult


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str = "", base_url: str = "") -> None:
        self._api_key = api_key
        self._base_url = base_url

    async def complete(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> ProviderResult:
        if not self._api_key:
            raise ProviderError(status=401, message="OPENAI_API_KEY not set")
        try:
            from openai import AsyncOpenAI
        except ImportError:  # pragma: no cover - exercised only without the SDK
            raise ProviderError(status=501, message="openai SDK not installed")

        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url or None)
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}] + messages,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", 502) or 502
            raise ProviderError(status=status, message=str(exc)) from exc
        finally:
            await client.close()

        choice = resp.choices[0]
        usage = getattr(resp, "usage", None)
        return ProviderResult(
            content=choice.message.content or "",
            model=getattr(resp, "model", model),
            tokens_used=getattr(usage, "total_tokens", 0) if usage else 0,
        )
