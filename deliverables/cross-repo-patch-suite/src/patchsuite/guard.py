"""Overwrite guard.

Repo policy: existing work is never silently replaced. An append is additive and
safe by definition; a create is safe when the path is free; a *replace* is the
only operation that needs an explicit human decision, and it is refused here
unless the caller passes ``approval`` that names the file.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path

from . import eol


class Intent(str, enum.Enum):
    CREATE = "create"
    APPEND = "append"
    REPLACE = "replace"


class Decision(str, enum.Enum):
    ALLOW = "allow"
    REFUSE = "refuse"


@dataclass
class GuardResult:
    path: str
    intent: str
    decision: str
    exists: bool
    existing_bytes: int
    existing_sha256: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.decision == Decision.ALLOW.value

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "intent": self.intent,
            "decision": self.decision,
            "exists": self.exists,
            "existing_bytes": self.existing_bytes,
            "existing_sha256": self.existing_sha256,
            "reason": self.reason,
            "allowed": self.allowed,
        }


def guard(path: str | Path, intent: Intent | str, approval: str | None = None) -> GuardResult:
    """Decide whether a write may proceed, and say why.

    ``approval`` must be the exact path being replaced — a blanket 'yes' is not
    sufficient, because the point is to force the specific file into view.
    """
    p = Path(path)
    intent = Intent(intent) if not isinstance(intent, Intent) else intent
    exists = p.exists()
    raw = p.read_bytes() if exists else b""
    prof = eol.profile(raw)

    if intent is Intent.CREATE:
        if exists:
            return GuardResult(
                str(p),
                intent.value,
                Decision.REFUSE.value,
                True,
                prof.size,
                prof.sha256,
                "File already exists. Create the new work under a different name "
                "rather than overwriting it, or change the intent to replace with "
                "explicit approval.",
            )
        return GuardResult(str(p), intent.value, Decision.ALLOW.value, False, 0, "", "Path is free.")

    if intent is Intent.APPEND:
        return GuardResult(
            str(p),
            intent.value,
            Decision.ALLOW.value,
            exists,
            prof.size,
            prof.sha256,
            "Append is additive — existing bytes are preserved by construction.",
        )

    if approval != str(path):
        return GuardResult(
            str(p),
            intent.value,
            Decision.REFUSE.value,
            exists,
            prof.size,
            prof.sha256,
            "Replace requires approval naming this exact path.",
        )
    return GuardResult(
        str(p),
        intent.value,
        Decision.ALLOW.value,
        exists,
        prof.size,
        prof.sha256,
        "Replace approved for this path.",
    )


@dataclass
class PlannedWrite:
    path: str
    intent: str
    decision: str
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "intent": self.intent,
            "decision": self.decision,
            "reason": self.reason,
        }


def plan_writes(files: dict[str, Intent | str], approvals: set[str] | None = None) -> list[PlannedWrite]:
    """Check a whole changeset before writing any of it."""
    approvals = approvals or set()
    out: list[PlannedWrite] = []
    for path, intent in files.items():
        result = guard(path, intent, approval=path if path in approvals else None)
        out.append(PlannedWrite(result.path, result.intent, result.decision, result.reason))
    return out


def all_allowed(plan: list[PlannedWrite]) -> bool:
    return all(p.decision == Decision.ALLOW.value for p in plan)
