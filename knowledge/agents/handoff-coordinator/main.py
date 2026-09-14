"""Handoff Coordinator -- validate work passing between owners."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

#: Fields every handoff must carry for the receiver to act.
REQUIRED_FIELDS = (
    "summary",
    "artifacts",
    "acceptance_criteria",
    "next_action",
)


@dataclass
class Handoff:
    """A unit of work passing from one owner to another."""

    work_id: str
    from_owner: str
    to_owner: str
    summary: str = ""
    artifacts: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    next_action: str = ""
    open_questions: List[str] = field(default_factory=list)

    def field_value(self, name: str) -> object:
        return getattr(self, name)


class HandoffCoordinator:
    """Gate handoffs on completeness.

    Args:
        require_open_questions: When true, unresolved questions block the handoff.
    """

    def __init__(self, require_open_questions: bool = False) -> None:
        self.require_open_questions = require_open_questions

    def validate(self, handoff: Handoff) -> List[str]:
        """Return a list of problems; empty means the handoff is ready."""
        problems: List[str] = []
        for name in REQUIRED_FIELDS:
            value = handoff.field_value(name)
            if isinstance(value, list):
                if not value:
                    problems.append(f"{name} is empty")
            elif not str(value).strip():
                problems.append(f"{name} is empty")
        if not handoff.to_owner.strip():
            problems.append("to_owner is empty")
        if handoff.from_owner == handoff.to_owner:
            problems.append("from_owner and to_owner are the same")
        if self.require_open_questions and handoff.open_questions:
            problems.append(
                f"{len(handoff.open_questions)} unresolved question(s) must be closed"
            )
        return problems

    def accept(self, handoff: Handoff) -> bool:
        """True when the handoff may proceed."""
        return not self.validate(handoff)

    def receipt(self, handoff: Handoff) -> Dict[str, object]:
        """Render an accept/reject receipt the receiver can act on."""
        problems = self.validate(handoff)
        return {
            "work_id": handoff.work_id,
            "from": handoff.from_owner,
            "to": handoff.to_owner,
            "status": "accepted" if not problems else "rejected",
            "problems": problems,
            "artifact_count": len(handoff.artifacts),
            "criteria_count": len(handoff.acceptance_criteria),
            "receiver_next_step": handoff.next_action if not problems else None,
        }

    def batch(self, handoffs: Sequence[Handoff]) -> Dict[str, object]:
        """Summarize a set of handoffs."""
        receipts = [self.receipt(h) for h in handoffs]
        rejected = [r["work_id"] for r in receipts if r["status"] == "rejected"]
        return {
            "total": len(handoffs),
            "accepted": len(receipts) - len(rejected),
            "rejected": len(rejected),
            "rejected_ids": sorted(rejected),
            "receipts": receipts,
        }
