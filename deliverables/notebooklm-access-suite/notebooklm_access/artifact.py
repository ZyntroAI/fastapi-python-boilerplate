"""artifact-router — detect /artifact/<id> and route to the parent notebook.

Read-only: returns artifact metadata and the canonical notebook URL without
fetching artifact content.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .resolver import ResolverError, canonical_url, extract_artifact


def route_artifact(raw_url: str) -> Dict[str, Any]:
    """Return routing decision: artifact metadata + parent notebook URL."""
    try:
        artifact_id = extract_artifact(raw_url)
    except ResolverError:
        return {"routed": False, "reason": "invalid_url", "canonical_url": None,
                "artifact_metadata": None}
    if artifact_id is None:
        return {"routed": False, "reason": "no_artifact",
                "canonical_url": canonical_url(raw_url),
                "artifact_metadata": None}
    canon = canonical_url(raw_url)
    return {"routed": True, "reason": "artifact_to_notebook",
            "canonical_url": canon,
            "artifact_metadata": {"artifact_id": artifact_id,
                                  "parent_notebook": canon}}


def artifact_metadata(raw_url: str) -> Optional[Dict[str, Any]]:
    """Return artifact metadata only, or None if no artifact is present."""
    meta = route_artifact(raw_url)
    return meta.get("artifact_metadata")
