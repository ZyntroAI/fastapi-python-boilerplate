"""GitHub source — repo/PR lookups via the public API."""
from __future__ import annotations

from typing import Any, Dict, Optional


class GitHubSource:
    def __init__(self, http, token: Optional[str] = None) -> None:
        self._http = http
        self._token = token

    def _headers(self) -> Optional[Dict[str, str]]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return None

    async def repo(self, repo: str, **kw: Any) -> Dict[str, Any]:
        return await self._http.get(f"https://api.github.com/repos/{repo}",
                                    headers=self._headers())

    async def pr(self, repo: str, number: int, **kw: Any) -> Dict[str, Any]:
        return await self._http.get(f"https://api.github.com/repos/{repo}/pulls/{number}",
                                    headers=self._headers())
