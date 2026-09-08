"""Fetching skill — SSRF-safe async HTTP/GraphQL fetch with retry + cache + provenance.

Usage:
    from skills.fetching import fetch
    data = await fetch.json("https://api.example.com/data")
    cached = await fetch.cached("https://docs.example.com", ttl=120)
"""
from __future__ import annotations

from typing import Any, Optional

from .clients.http import HTTPClient
from .clients.graphql import GraphQLClient
from .clients.websocket import WebSocketClient
from .reliability.cache import Cache
from .security.ssrf import check as ssrf_check
from .sources.github import GitHubSource


class FetchingSkill:
    def __init__(self) -> None:
        self.http = HTTPClient()
        self.graphql = GraphQLClient()
        self.websocket = WebSocketClient()
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



    async def gql(self, endpoint: str, query: str, **kw: Any):
        return await self.graphql.execute(endpoint, query, **kw)

    async def ws_connect(self, url: str, **kw: Any):
        return await self.websocket.connect(url, **kw)

    async def ws_send(self, msg: Any):
        return await self.websocket.send(msg)

    async def ws_receive(self):
        async for m in self.websocket.receive():
            yield m

    async def ws_close(self):
        return await self.websocket.close()


fetch = FetchingSkill()

__all__ = ["FetchingSkill", "fetch"]
