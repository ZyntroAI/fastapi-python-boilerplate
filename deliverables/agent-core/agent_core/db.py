"""Supabase persistence for agent tasks.

Uses PostgREST over ``httpx`` rather than pulling in the Supabase SDK — one
fewer dependency, and the service key stays server-side.  The SQL that must be
applied once lives in ``schema.sql``.
"""
from __future__ import annotations

from typing import Any

import httpx

from .config import get_settings
from .errors import AgentAPIError


class TaskStore:
    """Thin, injectable repository over the ``agent_tasks`` table."""

    TABLE = "agent_tasks"

    def __init__(
        self,
        base_url: str | None = None,
        service_key: str | None = None,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if base_url is None or service_key is None:
            base_url, service_key = get_settings().require_supabase()
        self.base_url = base_url.rstrip("/")
        self._headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._owns_client = client is None

    def _url(self, path: str = "") -> str:
        return f"{self.base_url}/rest/v1/{self.TABLE}{path}"

    def _check(self, resp: httpx.Response) -> httpx.Response:
        if resp.status_code >= 400:
            raise AgentAPIError(resp.status_code, resp.text[:500])
        return resp

    async def save(self, record: dict[str, Any]) -> dict[str, Any]:
        """Insert (or upsert on ``agent_task_id``) a task row."""
        resp = await self._client.post(
            self._url(),
            headers={**self._headers, "Prefer": "resolution=merge-duplicates,return=representation"},
            json=[record],
        )
        self._check(resp)
        rows = resp.json()
        return rows[0] if rows else record

    async def get(self, agent_task_id: str) -> dict[str, Any] | None:
        resp = await self._client.get(
            self._url(),
            headers=self._headers,
            params={"agent_task_id": f"eq.{agent_task_id}", "limit": "1"},
        )
        self._check(resp)
        rows = resp.json()
        return rows[0] if rows else None

    async def list_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        resp = await self._client.get(
            self._url(),
            headers=self._headers,
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "limit": str(limit),
            },
        )
        self._check(resp)
        return resp.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
