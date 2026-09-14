"""Minimal MCP client wrapper (lazy `mcp` import).

Connects over stdio transport and calls tools. mcp is imported lazily.
"""
from __future__ import annotations

from typing import Any, Dict


class MCPClient:
    def __init__(self, command: list) -> None:
        from mcp.client import Client
        from mcp.client.transport import StdioTransport
        self._transport = StdioTransport(command=command)
        self._client = Client(self._transport)

    async def connect(self) -> None:
        await self._client.connect()

    async def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        return await self._client.call_tool(name, params)

    async def close(self) -> None:
        await self._client.close()
