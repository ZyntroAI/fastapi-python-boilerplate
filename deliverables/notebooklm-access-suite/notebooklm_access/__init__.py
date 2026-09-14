"""NotebookLM Access + Artifact Intelligence.

Pipeline: link-resolver -> artifact-router -> access-check -> share-validator
-> (guide / verify / security / provenance / knowledge). Read-only,
evidence-based. No auth bypass, no permission change.
"""
from __future__ import annotations

from .resolver import resolve, canonical_url, extract_artifact
from .access import classify_access, AccessState, report
from .artifact import route_artifact, artifact_metadata
from .validate import validate_share
from .guide import remediation_steps, next_action
from .link_security import check_link
from .provenance import ProvenanceLog
from .knowledge import build_knowledge_artifact

__all__ = ["resolve", "canonical_url", "extract_artifact", "classify_access",
           "AccessState", "report", "route_artifact", "artifact_metadata",
           "validate_share", "remediation_steps", "next_action", "check_link",
           "ProvenanceLog", "build_knowledge_artifact"]
