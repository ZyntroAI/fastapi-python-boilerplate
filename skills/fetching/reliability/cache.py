"""In-memory TTL cache keyed by SHA-256 of the URL."""
from __future__ import annotations

import hashlib
import time
from typing import Any, Optional


class Cache:
    def __init__(self, default_ttl: int = 300) -> None:
        self.default_ttl = default_ttl
        self._store: dict[str, dict] = {}

    def key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        v = self._store.get(key)
        if not v or v["exp"] < time.time():
            return None
        return v["data"]

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = {"data": data, "exp": time.time() + (ttl or self.default_ttl)}

    def clear(self) -> None:
        self._store.clear()
