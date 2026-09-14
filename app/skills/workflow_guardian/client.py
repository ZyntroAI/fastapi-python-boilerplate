"""Workflow Guardian skill client — permission-aware git + SHA-pin.

Delegates secret resolution to the central credential broker; this module
never holds tokens. Mirrors the standalone guardian concept as a thin client
that calls the shared broker for github credentials.
"""
from __future__ import annotations

from typing import Dict, List

from app.core.credential_broker import credential_broker


class WorkflowGuardian:
    async def check_permissions(self, files: List[str]) -> Dict:
        """Ask the broker whether we may push the given files (detect workflows)."""
        needs_workflow = any(f.startswith(".github/workflows/") for f in files)
        scopes = ["contents:write"] + (["workflows:write"] if needs_workflow else [])
        req = {
            "skill": "workflow-guardian",
            "provider": "github",
            "operation": ["repo:push"],
            "required_scopes": scopes,
        }
        cred = await credential_broker.resolve(type("R", (), {"model_dump": lambda s: req})())
        scope_ok = cred.get("scope_ok", False)
        return {
            "status": "OK" if scope_ok else "BLOCKED",
            "needs_workflow_write": needs_workflow,
            "can_push": scope_ok,
        }


workflow_guardian = WorkflowGuardian()
