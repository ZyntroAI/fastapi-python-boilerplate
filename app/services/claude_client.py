"""
Claude API client — provider-neutral wrapper over the Anthropic Messages API.

Uses httpx directly rather than the `anthropic` SDK so the app gains no new
hard dependency; the wire format is the stable part.

Two entry points, matching the two endpoint shapes:
  - stream_message(...)  -> async generator of raw SSE events
  - send_message(...)    -> awaited full JSON response
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"


def _setting(name: str, default: str = "") -> str:
    """
    Read one setting without importing app.core.config at module scope.

    Importing `settings` eagerly would run Settings() at import time, which
    fails on any environment whose .env carries keys the model does not declare.
    Keeping this lazy means the client is importable (and testable) regardless.
    """
    try:
        from app.core.config import settings
    except Exception:
        return default
    return getattr(settings, name, default) or default


class ClaudeClientError(RuntimeError):
    """Raised when the upstream Claude API cannot be reached or rejects the call."""


class ClaudeClient:
    """Thin async client for the Anthropic Messages API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or _setting("ANTHROPIC_API_KEY", "")
        self.base_url = (base_url or _setting("ANTHROPIC_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.default_model = default_model or _setting("CLAUDE_MODEL", "claude-sonnet-4-6")
        self.timeout = timeout

    # ── internals ──────────────────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise ClaudeClientError(
                "ANTHROPIC_API_KEY is not configured — set it in the environment to call Claude."
            )
        return {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

    def _body(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str],
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": model or self.default_model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            body["tools"] = tools
        return body

    # ── public API ─────────────────────────────────────────────────────────

    async def send_message(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Single non-streaming call. Returns the raw Anthropic JSON body."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/messages",
                headers=self._headers(),
                json=self._body(messages, model, max_tokens, tools, stream=False),
            )
        if resp.status_code >= 400:
            raise ClaudeClientError(f"Claude API returned {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Streaming call. Yields each decoded SSE `data:` payload as a dict."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers=self._headers(),
                json=self._body(messages, model, max_tokens, tools, stream=True),
            ) as resp:
                if resp.status_code >= 400:
                    detail = (await resp.aread()).decode(errors="replace")[:300]
                    raise ClaudeClientError(f"Claude API returned {resp.status_code}: {detail}")

                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    payload = line[len("data:"):].strip()
                    if not payload or payload == "[DONE]":
                        continue
                    try:
                        yield json.loads(payload)
                    except json.JSONDecodeError:
                        # Keep transport tolerant: skip frames we cannot decode
                        # rather than killing the whole stream.
                        continue


def get_claude_client() -> ClaudeClient:
    """FastAPI dependency — overridable in tests."""
    return ClaudeClient()
