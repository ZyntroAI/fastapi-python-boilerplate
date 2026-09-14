"""share-guide — read-only remediation guidance. Never modifies permissions."""
from __future__ import annotations

from typing import Dict, List


def remediation_steps() -> List[str]:
    return [
        "open_notebook",
        "set_anyone_with_link",
        "role_viewer",
        "save",
        "test_incognito",
    ]


def next_action(state: str) -> Dict[str, str]:
    if state in ("RESTRICTED", "PRIVATE"):
        return {"type": "CHANGE_SHARING", "actor": "OWNER", "guide": " ".join(remediation_steps())}
    if state == "PUBLIC":
        return {"type": "NONE", "actor": "NONE", "guide": "already public"}
    return {"type": "NONE", "actor": "NONE", "guide": "check url/evidence"}
