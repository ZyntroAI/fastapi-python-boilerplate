"""Async HTTP client (httpx) — SSRF-guarded, timeout, wraps provenance."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from ..security.ssrf import check as ssrf_check


class HTTPError(Exception):
    pass


class HTTPClient:
    def __init__(self, timeout: float = 30.0, max_redirects: int = 5) -> None:
        self.timeout = timeout
        self.max_redirects = max_redirects

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kw: Any) -> Dict[str, Any]:
        ssrf_check(url)  # raise before any request if blocked
        async with httpx.AsyncClient(timeout=self.timeout,
                                     follow_redirects=True,
                                     max_redirects=self.max_redirects) as c:
            r = await c.get(url, headers=headers)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPError(f"GET {url} -> {e.response.status_code}") from e
            content = r.content
            return {
                "status": r.status_code,
                "text": r.text,
                "json": r.json() if "json" in (r.headers.get("content-type", "") or "") else None,
                "url": str(r.url),
                "provenance": {
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "checksum": "sha256:" + hashlib.sha256(content).hexdigest(),
                    "content_type": r.headers.get("content-type"),
                    "final_url": str(r.url),
                },
            }
