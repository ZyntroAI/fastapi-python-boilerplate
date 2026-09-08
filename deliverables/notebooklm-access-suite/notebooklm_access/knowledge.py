"""link-to-knowledge — build a knowledge artifact when a link is PUBLIC_OK."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict


def build_knowledge_artifact(canonical_url: str, resource: Dict[str, Any],
                             register: bool = True) -> Dict[str, Any]:
    """Create a knowledge artifact (and optionally note registry intent)."""
    if not resource.get("canonical_url"):
        resource = {**resource, "canonical_url": canonical_url}
    artifact = {
        "artifact_id": hashlib.sha256(resource["canonical_url"].encode()).hexdigest()[:16],
        "provider": resource.get("provider", "notebooklm"),
        "canonical_url": resource["canonical_url"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "registered": register,
    }
    return artifact
