"""Minimal async client for the Obsidian Local REST API (HTTPS + Bearer).

Requires the "Local REST API" community plugin. Token and base URL come from
app settings (or env). Used by the indexer scripts; kept dependency-light so it
runs anywhere (aiohttp).
"""
from __future__ import annotations

import os
from typing import Any

import aiohttp

BASE = os.environ.get("OBSIDIAN_API_URL", "https://127.0.0.1:27124")
TOKEN = os.environ.get("OBSIDIAN_API_TOKEN", "")

_SSL_CONTEXT = None
try:
    import ssl

    # The plugin ships a self-signed cert by default; allow override.
    if os.environ.get("OBSIDIAN_VERIFY_SSL", "1") != "1":
        _SSL_CONTEXT = ssl.create_default_context()
        _SSL_CONTEXT.check_hostname = False
        _SSL_CONTEXT.verify_mode = ssl.CERT_NONE
except Exception:  # noqa: BLE001 - ssl unavailable
    pass


async def _request(method: str, path: str, **kw: Any) -> Any:
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(connector_ssl=_SSL_CONTEXT) as session:
        async with session.request(method, f"{BASE}{path}", headers=headers, **kw) as resp:
            resp.raise_for_status()
            if resp.status == 204:
                return None
            return await resp.json()


async def list_vault_files() -> list[str]:
    """List vault files as markdown paths relative to the vault root."""
    data = await _request("GET", "/vault/")
    return [f["path"] for f in data.get("files", []) if f.get("path", "").endswith(".md")]


async def read_vault_file(path: str) -> str:
    data = await _request("GET", f"/vault/{path}")
    return data.get("content", "")
