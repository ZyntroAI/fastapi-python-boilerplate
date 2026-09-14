"""access-check — multi-evidence, read-only access classification.

Classifies PUBLIC / RESTRICTED / PRIVATE / INVALID from evidence supplied by a
probe, without ever attempting auth bypass or permission change. The caller
supplies evidence (e.g. from an anonymous HTTP probe) via ``evidence``.
"""
from __future__ import annotations

from typing import Any, Dict, List

# Access states
PUBLIC = "PUBLIC"
RESTRICTED = "RESTRICTED"
PRIVATE = "PRIVATE"
INVALID = "INVALID"


class AccessState:
    PUBLIC = PUBLIC
    RESTRICTED = RESTRICTED
    PRIVATE = PRIVATE
    INVALID = INVALID


# Evidence signals -> meaning
_EVIDENCE = {
    "login_redirect": RESTRICTED,     # bounced to login => not anonymous-accessible
    "anonymous_fail": RESTRICTED,
    "artifact_denied": RESTRICTED,    # anonymous denied on artifact
    "login_page_detected": RESTRICTED,
    "ok_200_anon": PUBLIC,            # 200 anonymous => public
    "not_found": INVALID,             # 404 / bad id
    "requires_account": PRIVATE,      # explicit private/account-only gate
}


def classify_access(evidence: List[str]) -> Dict[str, Any]:
    """Map evidence signals to an access state.

    Priority: INVALID beats PRIVATE beats RESTRICTED beats PUBLIC. Evidence not
    in the known set is ignored (no fabrication).
    """
    if not evidence:
        return {"state": "UNKNOWN", "anonymous": False,
                "login_required": True, "confidence": "low",
                "evidence": evidence}
    mapped = [_EVIDENCE[e] for e in evidence if e in _EVIDENCE]
    if INVALID in mapped:
        state = INVALID
    elif PRIVATE in mapped:
        state = PRIVATE
    elif any(m == RESTRICTED for m in mapped):
        state = RESTRICTED
    else:
        state = PUBLIC
    anonymous = state == PUBLIC
    return {
        "state": state,
        "anonymous": anonymous,
        "login_required": not anonymous,
        "confidence": "high" if mapped else "low",
        "evidence": evidence,
    }


def report(evidence: List[str]) -> Dict[str, Any]:
    """Public classifier wrapper returning a machine-readable access block."""
    c = classify_access(evidence)
    return {"access": c, "status": {"code": f"ACCESS_{c['state']}",
            "retryable": False, "user_action_required": c["state"] in (RESTRICTED, PRIVATE)}}
