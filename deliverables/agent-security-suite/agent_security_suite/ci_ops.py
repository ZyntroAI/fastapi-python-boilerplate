"""CI/CD operations — permission-aware checks + SHA-pin scan + root-cause fingerprint.

Pure-Python, runnable against a repo checkout (no GitHub API needed for the
core detections). Distilled from the real failure chain in this repo
(#125-#130 all failing at 'Set up job' from a single workflow YAML/permission
root cause) so callers stop probing-and-failing and check before acting.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------
# Permission-aware
# --------------------------------------------------------------------------
# Which GitHub App permission a given operation really needs. Key lesson:
# `contents: write` is NOT `workflows: write`.
OPERATION_PERMISSIONS = {
    "workflow_write": {"contents:write", "workflows:write"},
    "normal_code_write": {"contents:write"},
    "rerun_ci": {"actions:write"},
}


def required_permissions(operation: str) -> set:
    return set(OPERATION_PERMISSIONS.get(operation, {"contents:read"}))


def can_write(operation: str, granted: set) -> bool:
    """True only if every permission the operation needs is granted."""
    return required_permissions(operation) <= set(granted)


def explain(operation: str, granted: set) -> Dict[str, Any]:
    req = required_permissions(operation)
    missing = sorted(req - set(granted))
    return {
        "operation": operation,
        "required": sorted(req),
        "granted": sorted(granted),
        "missing": missing,
        "allowed": not missing,
    }


# --------------------------------------------------------------------------
# SHA-pin scan
# --------------------------------------------------------------------------
ACTION_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*([^\s@#]+)@([^\s#]+)", re.M)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def sha_pin_scan(workflow_text: str) -> Dict[str, Any]:
    """Return per-reference pin status. A reference is compliant when it uses
    a full 40-char SHA (not a tag like @v4 / @v5)."""
    refs = []
    for m in ACTION_RE.finditer(workflow_text):
        name, ver = m.group(1), m.group(2).rstrip()
        refs.append({"action": name, "ref": ver,
                     "sha_pinned": bool(SHA40.match(ver)),
                     "length": len(ver)})
    compliant = all(r["sha_pinned"] for r in refs) if refs else True
    return {"references": refs, "compliant": compliant,
            "total": len(refs), "unpinned": [r for r in refs if not r["sha_pinned"]]}


def sha_pin_scan_file(path: Path) -> Dict[str, Any]:
    try:
        return sha_pin_scan(path.read_text())
    except OSError as e:
        return {"error": str(e), "references": [], "compliant": False}


# --------------------------------------------------------------------------
# CI root-cause fingerprint
# --------------------------------------------------------------------------
# Heuristic fingerprints for common systemic failures across a batch of PRs.
FINGERPRINTS = {
    "SHA_PIN_POLICY": ["refusing to allow a GitHub App", "workflows", "permission"],
    "SETUP_JOB_YAML": ["set up job", "yaml", "parse", "syntax", "invalid"],
    "UNREACHABLE_HOST": ["could not resolve host", "connection refused", "getaddrinfo"],
}


def fingerprint_failure(text: str) -> Optional[str]:
    low = text.lower()
    for name, needles in FINGERPRINTS.items():
        if all(n.lower() in low for n in needles):
            return name
    return None


def classify_run(text: str) -> Dict[str, Any]:
    fp = fingerprint_failure(text)
    return {"fingerprint": fp,
            "systemic": fp is not None,
            "category": fp or "unknown"}


def diagnose_batch(logs: List[str]) -> Dict[str, Any]:
    """Given failure logs across PRs, detect if they share one root cause."""
    fps = [fingerprint_failure(t) for t in logs]
    real = [f for f in fps if f]
    shared = len(set(real)) == 1 and len(real) == len(logs) and len(logs) > 1
    return {"fingerprints": fps,
            "shared_root_cause": shared,
            "root_cause": real[0] if real and shared else None,
            "systemic": shared}
