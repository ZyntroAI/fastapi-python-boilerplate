"""NotebookLM Access + Artifact Intelligence — Core (P0).

Pipeline: link-resolver -> artifact-router -> access-check, each producing
evidence-based, read-only output. No auth bypass, no permission changes.

Core rule: never auto-change permissions; classify from evidence only.
"""
from __future__ import annotations

from .resolver import resolve, canonical_url, extract_artifact
from .access import classify_access, AccessState
from .artifact import route_artifact, artifact_metadata

__all__ = ["resolve", "canonical_url", "extract_artifact",
           "classify_access", "AccessState", "route_artifact", "artifact_metadata"]
