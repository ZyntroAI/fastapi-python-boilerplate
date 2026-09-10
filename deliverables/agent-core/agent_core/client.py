"""Agent provider client — real async I/O over httpx."""
from __future__ import annotations

from typing import Any

import httpx

from .base import TargetClient
from .config import get_settings
from .errors import (
    AgentAPIError,
    AgentAuthError,
    AgentRateLimitError,
    AgentTimeoutError,
)
from .retry import with_retry


class AgentClient(TargetClient):
    """Async client for the Agent API.

    One ``httpx.AsyncClient`` is shared across calls so connections are pooled;
    nothing here blocks the event loop.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
        retries: int | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.AGENT_BASE_URL).rstrip("/")
        self._api_key = api_key if api_key is not None else settings.AGENT_API_KEY
        self.timeout = timeout or settings.AGENT_TIMEOUT
        self.retries = retries or settings.AGENT_MAX_RETRIES
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=transport,
        )

    # -- internals -------------------------------------------------------
    def _headers(self) -> dict[str, str]:
        # Key travels in a header, never a query string (avoids proxy logs).
        if not self._api_key:
            raise AgentAuthError("AGENT_API_KEY is not set")
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code in (401, 403):
            raise AgentAuthError(f"authentication failed ({resp.status_code})")
        if resp.status_code == 429:
            raise AgentRateLimitError("rate limit exceeded (429)")
        if resp.status_code >= 400:
            raise AgentAPIError(resp.status_code, resp.text[:500])

    async def _request(self, method: str, url: str, **kw: Any) -> httpx.Response:
        async def call() -> httpx.Response:
            try:
                resp = await self._client.request(
                    method, url, headers=self._headers(), **kw
                )
            except httpx.TimeoutException as err:
                raise AgentTimeoutError(str(err)) from err
            self._raise_for_status(resp)
            return resp

        return await with_retry(call, retries=self.retries)

    # -- TargetClient ----------------------------------------------------
    async def submit(self, payload: dict[str, Any]) -> str:
        resp = await self._request("POST", "/tasks", json=payload)
        body = resp.json()
        try:
            return body["task_id"]
        except (KeyError, TypeError) as err:
            raise AgentAPIError(resp.status_code, "response had no task_id") from err

    async def status(self, task_id: str) -> str:
        resp = await self._request("GET", f"/tasks/{task_id}")
        return resp.json().get("status", "unknown")

    async def result(self, task_id: str) -> dict[str, Any] | None:
        # Retried like the others — a transient blip here would otherwise throw
        # away an already-completed task's output.
        resp = await self._request("GET", f"/tasks/{task_id}/result")
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AgentClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
