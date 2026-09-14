"""share-validator — validate a NotebookLM share link's structure + state.

Read-only classification combining resolver structure and access evidence.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .access import classify_access
from .resolver import canonical_url, ResolverError


def validate_share(url: str, evidence: List[str]) -> Dict[str, Any]:
    """Return a machine-readable share_state."""
    try:
        canonical_url(url)
    except ResolverError:
        return {"share_state": "URL_INVALID", "valid": False, "canonical_url": None}
    acc = classify_access(evidence)
    if acc["state"] in ("PUBLIC",):
        state = "PUBLIC_OK"
    elif acc["state"] in ("RESTRICTED", "PRIVATE"):
        state = "NOT_PUBLIC"
    else:
        state = "URL_INVALID" if acc["state"] == "INVALID" else "UNKNOWN"
    return {"share_state": state, "valid": state == "PUBLIC_OK",
            "canonical_url": canonical_url(url), "access": acc}
