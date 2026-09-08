"""Credential Management skill client — wraps the central broker.

No secrets here; every call resolves a short-lived lease via the broker.
"""
from __future__ import annotations

from typing import Dict, List

from app.core.credential_broker import credential_broker
from app.core.credential_broker import CredentialRequest


class CredentialManagement:
    async def resolve(self, skill: str, provider: str, operation: List[str],
                      required_scopes: List[str], duration: str = "15m") -> Dict:
        req = CredentialRequest(
            skill=skill, provider=provider, operation=operation,
            required_scopes=required_scopes, duration=duration,
        )
        return await credential_broker.resolve(req)

    async def health(self) -> Dict:
        return await credential_broker.health()


credential_management = CredentialManagement()
