"""Fetching skill — SSRF-safe async HTTP/GraphQL fetch with retry + cache + provenance.

Usage:
    from skills.fetching import fetch
    data = await fetch.json("https://api.example.com/data")
    cached = await fetch.cached("https://docs.example.com", ttl=120)
"""
from __future__ import annotations

from typing import Any, Optional

from .clients.http import HTTPClient
from .reliability.cache import Cache
from .security.ssrf import check as ssrf_check
from .sources.github import GitHubSource


class FetchingSkill:
    def __init__(self) -> None:
        self.http = HTTPClient()
        self.cache = Cache()
        self.github = GitHubSource(self.http)

    async def url(self, url: str, **kw: Any):
        ssrf_check(url)
        return await self.http.get(url, **kw)

    async def json(self, url: str, **kw: Any):
        res = await self.url(url, **kw)
        if res["json"] is None:
            import json as _json
            res["json"] = _json.loads(res["text"])
        return res["json"]

    async def cached(self, url: str, ttl: Optional[int] = None, **kw: Any):
        key = self.cache.key(url)
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        data = await self.url(url, **kw)
        self.cache.set(key, data, ttl)
        return data


fetch = FetchingSkill()

__all__ = ["FetchingSkill", "fetch"]
