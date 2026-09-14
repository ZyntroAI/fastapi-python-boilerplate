"""Async WebSocket client — SSRF-guarded, lazy websockets lib, provenance.

Uses the `websockets` library, imported lazily at connect time so the skill
has no hard dependency on it until a WS connection is actually opened.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

from ..security.ssrf import check_ws as ssrf_check_ws


class WebSocketClient:
    def __init__(self) -> None:
        self._conn: Optional[Dict[str, Any]] = None
        self._ws = None

    async def connect(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        ssrf_check_ws(url)  # wss/ws only + SSRF host guard
        import websockets  # lazy: only needed for a real connection

        extra_headers = headers or {}
        ws = await websockets.connect(url, additional_headers=extra_headers)
        self._ws = ws
        self._conn = {"url": url, "headers": extra_headers, "provenance": {
            "url": url,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "type": "websocket",
            "fetched_by": "fetching.websocket",
        }}
        return self._wrap("connected")

    async def send(self, message: Any) -> Dict[str, Any]:
        if self._ws is None:
            raise ConnectionError("WebSocket not connected")
        await self._ws.send(message)
        return self._wrap("sent", message=message)

    async def receive(self) -> AsyncGenerator[Dict[str, Any], None]:
        if self._ws is None:
            raise ConnectionError("WebSocket not connected")
        async for msg in self._ws:
            yield self._wrap("message", message=msg)

    async def close(self) -> Dict[str, Any]:
        if self._ws is not None:
            await self._ws.close()
        self._ws = None
        self._conn = None
        return self._wrap("closed")

    def _wrap(self, status: str, message: Any = None) -> Dict[str, Any]:
        prov = (self._conn or {}).get("provenance", {})
        out: Dict[str, Any] = {"status": status, "message": message, "provenance": dict(prov)}
        out["provenance"]["last_action"] = status
        if not self._conn:
            out["provenance"] = {**prov, "type": "websocket"}
        return out
