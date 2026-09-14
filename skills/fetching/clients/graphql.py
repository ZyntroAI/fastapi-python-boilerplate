"""Async GraphQL client — SSRF-guarded POST with optional cache + provenance."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from ..reliability.cache import Cache
from ..reliability.retry import retry
from ..security.ssrf import check as ssrf_check


class GraphQLClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.cache = Cache()

    @retry(max_attempts=3)
    async def execute(
        self,
        endpoint: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        ssrf_check(endpoint)  # HTTPS-only + SSRF host guard before any request

        payload: Dict[str, Any] = {"query": query, "variables": variables or {}}
        req_headers = dict(headers or {})
        req_headers.setdefault("Content-Type", "application/json")

        cache_key = self.cache.key(f"graphql:{endpoint}:{query}:{variables}")
        if cache_ttl:
            hit = self.cache.get(cache_key)
            if hit is not None:
                return self._wrap(hit, endpoint, cache_key, "HIT")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(endpoint, json=payload, headers=req_headers)
            resp.raise_for_status()
            data = resp.json()

        if cache_ttl:
            self.cache.set(cache_key, data, ttl=cache_ttl)

        return self._wrap(data, endpoint, cache_key, "MISS" if cache_ttl else None)

    async def query(self, endpoint: str, query: str, **kw: Any) -> Dict[str, Any]:
        return await self.execute(endpoint, query, **kw)

    async def mutation(self, endpoint: str, query: str, **kw: Any) -> Dict[str, Any]:
        return await self.execute(endpoint, query, **kw)

    @staticmethod
    def _wrap(data: Any, url: str, cache_key: str, cache_status: Optional[str]) -> Dict[str, Any]:
        return {
            "data": data,
            "provenance": {
                "url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "type": "graphql",
                "cache_key": cache_key,
                "cache": cache_status,
                "fetched_by": "fetching.graphql",
            },
        }
