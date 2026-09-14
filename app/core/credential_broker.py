"""Central credential broker client — resolves short-lived leases.

No raw secrets live in this repo. The broker talks to an external vault /
secret manager; this module only carries the *reference* configuration and
never exposes secret values to callers.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel

from app.core.config import settings

# Broker may be absent in local/test env; keep module importable.
_BROKER_URL: Optional[str] = getattr(settings, "CREDENTIAL_BROKER_URL", None)
_BROKER_TOKEN: Optional[str] = getattr(settings, "BROKER_TOKEN", None)


class CredentialRequest(BaseModel):
    skill: str
    provider: str
    operation: List[str]
    required_scopes: List[str]
    duration: str = "15m"


class CredentialBroker:
    """Thin async client. Every method tolerates a missing/unreachable broker
    and returns a structured status rather than raising, so the app still boots
    in local/test when the broker isn't deployed."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None) -> None:
        self.endpoint = (url or _BROKER_URL or "").rstrip("/")
        self.token = token or _BROKER_TOKEN or ""

    async def resolve(self, req: CredentialRequest) -> Dict:
        if not self.endpoint:
            return {"status": "unconfigured", "lease_id": None, "scope_ok": False}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.post(
                    f"{self.endpoint}/resolve",
                    json=req.model_dump(),
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception:
            return {"status": "unreachable", "lease_id": None, "scope_ok": False}

    async def lease(self, cred_id: str, duration: str = "10m") -> Optional[str]:
        if not self.endpoint:
            return None
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(
                    f"{self.endpoint}/lease",
                    json={"id": cred_id, "duration": duration},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                r.raise_for_status()
                return r.json().get("lease_id")
        except Exception:
            return None

    async def release(self, lease_id: str) -> bool:
        if not self.endpoint:
            return False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(
                    f"{self.endpoint}/release",
                    json={"lease_id": lease_id},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                return r.status_code < 300
        except Exception:
            return False

    async def health(self) -> Dict:
        if not self.endpoint:
            return {"status": "unconfigured"}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3) as c:
                r = await c.get(f"{self.endpoint}/health")
                return r.json()
        except Exception:
            return {"status": "unreachable"}


credential_broker = CredentialBroker()
