"""Anthropic provider — lazy SDK import, mirrors the OpenAI contract."""
from __future__ import annotations

from typing import Dict, List

from .base import BaseProvider, ProviderError, ProviderResult


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key

    async def complete(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> ProviderResult:
        if not self._api_key:
            raise ProviderError(status=401, message="ANTHROPIC_API_KEY not set")
        try:
            from anthropic import AsyncAnthropic
        except ImportError:  # pragma: no cover
            raise ProviderError(status=501, message="anthropic SDK not installed")

        client = AsyncAnthropic(api_key=self._api_key)
        try:
            resp = await client.messages.create(
                model=model,
                system=system,
                messages=messages,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", 502) or 502
            raise ProviderError(status=status, message=str(exc)) from exc
        finally:
            await client.close()

        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        usage = getattr(resp, "usage", None)
        used = (getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)) if usage else 0
        return ProviderResult(content=text, model=getattr(resp, "model", model), tokens_used=used)
