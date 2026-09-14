"""Blocker Resolver -- obstacle classification and recovery routing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

#: Resolution playbook keyed by blocker category.
PLAYBOOK: Dict[str, str] = {
    "dependency": "pin the missing dependency or vendor the interface",
    "permission": "request the scope from the resource owner; do not retry blindly",
    "environment": "rebuild the environment from its recorded recipe",
    "data": "locate the authoritative source and re-derive",
    "unclear_requirement": "return to the requester with one specific question",
    "external_service": "wait with backoff, then report the outage with evidence",
}

#: Categories that can never be cleared without a human decision.
ESCALATE_ALWAYS = frozenset({"permission", "unclear_requirement"})

#: Attempts allowed before an otherwise-resolvable blocker escalates.
MAX_SELF_ATTEMPTS = 2


@dataclass
class Blocker:
    """One obstacle holding up work."""

    id: str
    description: str
    category: str
    attempts: int = 0
    waiting_on: Optional[str] = None

    def __post_init__(self) -> None:
        if self.category not in PLAYBOOK:
            raise ValueError(
                f"unknown category {self.category!r}; "
                f"expected one of {sorted(PLAYBOOK)}"
            )


@dataclass
class Resolution:
    """The recommended action for one blocker."""

    blocker_id: str
    category: str
    action: str
    escalate: bool
    escalate_to: Optional[str] = None
    owner_blocked: bool = False


class BlockerResolver:
    """Route blockers to a resolution or an escalation.

    Args:
        max_self_attempts: Retries before a blocker escalates anyway.
    """

    def __init__(self, max_self_attempts: int = MAX_SELF_ATTEMPTS) -> None:
        if max_self_attempts < 0:
            raise ValueError("max_self_attempts cannot be negative")
        self.max_self_attempts = max_self_attempts

    def resolve(self, blocker: Blocker) -> Resolution:
        """Classify one blocker and recommend an action."""
        must_escalate = blocker.category in ESCALATE_ALWAYS
        exhausted = blocker.attempts >= self.max_self_attempts
        escalate = must_escalate or exhausted

        if escalate:
            action = (
                f"escalate to {blocker.waiting_on or 'the blocker owner'}: "
                f"{PLAYBOOK[blocker.category]}"
            )
        else:
            action = PLAYBOOK[blocker.category]

        return Resolution(
            blocker_id=blocker.id,
            category=blocker.category,
            action=action,
            escalate=escalate,
            escalate_to=blocker.waiting_on,
            owner_blocked=blocker.waiting_on is not None,
        )

    def triage(self, blockers: Sequence[Blocker]) -> Dict[str, object]:
        """Resolve a whole set and split what you can fix from what you cannot."""
        resolutions = [self.resolve(b) for b in blockers]
        needs_human = [r for r in resolutions if r.escalate]
        return {
            "total": len(blockers),
            "self_resolvable": len(resolutions) - len(needs_human),
            "needs_escalation": len(needs_human),
            "escalation_ids": [r.blocker_id for r in needs_human],
            "resolutions": {
                r.blocker_id: {
                    "category": r.category,
                    "action": r.action,
                    "escalate": r.escalate,
                }
                for r in resolutions
            },
        }
