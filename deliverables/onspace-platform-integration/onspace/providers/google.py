"""Google (Gemini) provider — lazy SDK import, mirrors the shared contract."""
from __future__ import annotations

from typing import Dict, List

from .base import BaseProvider, ProviderError, ProviderResult


class GoogleProvider(BaseProvider):
    name = "google"

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key

    async def complete(
        self, system: str, messages: List[Dict], model: str, max_tokens: int
    ) -> ProviderResult:
        if not self._api_key:
            raise ProviderError(status=401, message="GOOGLE_API_KEY not set")
        try:
            from google import genai
        except ImportError:  # pragma: no cover
            raise ProviderError(status=501, message="google-genai SDK not installed")

        client = genai.Client(api_key=self._api_key)

        def _to_dict(m: Dict) -> Dict:
            # Gemini uses "model" for the assistant role.
            role = "model" if m.get("role") == "assistant" else m.get("role", "user")
            return {"role": role, "parts": [{"text": m.get("content", "")}]}

        try:
            resp = await client.aio.models.generate_content(
                model=model,
                contents=[_to_dict(m) for m in messages],
                config={"system_instruction": system, "max_output_tokens": max_tokens},
            )
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "code", 502) or 502
            raise ProviderError(status=int(status) if str(status).isdigit() else 502, message=str(exc)) from exc

        usage = getattr(resp, "usage_metadata", None)
        used = getattr(usage, "total_token_count", 0) if usage else 0
        return ProviderResult(content=resp.text or "", model=model, tokens_used=used)
