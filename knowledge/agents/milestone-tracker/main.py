"""Milestone Tracker -- phase progress and timeline health."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass
class Milestone:
    """One phase of a plan."""

    id: str
    name: str
    planned_days: float
    actual_days: float = 0.0
    complete: bool = False

    @property
    def slip_days(self) -> float:
        """Days over (positive) or under (negative) the plan."""
        return round(self.actual_days - self.planned_days, 2)

    @property
    def progress(self) -> float:
        """Fraction of the planned duration consumed, capped at 1.0."""
        if self.planned_days <= 0:
            return 1.0 if self.complete else 0.0
        return round(min(self.actual_days / self.planned_days, 1.0), 4)


class MilestoneTracker:
    """Grade timeline health across phases.

    Args:
        at_risk_slip_ratio: Slip fraction that escalates a phase to at-risk.
        delayed_slip_ratio: Slip fraction that escalates a phase to delayed.
    """

    def __init__(
        self, at_risk_slip_ratio: float = 0.15, delayed_slip_ratio: float = 0.4
    ) -> None:
        if at_risk_slip_ratio >= delayed_slip_ratio:
            raise ValueError("at_risk threshold must be below the delayed threshold")
        self.at_risk_slip_ratio = at_risk_slip_ratio
        self.delayed_slip_ratio = delayed_slip_ratio

    def grade(self, milestone: Milestone) -> str:
        """Grade one milestone: complete | delayed | at_risk | on_track."""
        if milestone.complete:
            return "complete"
        if milestone.planned_days <= 0:
            return "at_risk"
        ratio = milestone.slip_days / milestone.planned_days
        if ratio >= self.delayed_slip_ratio:
            return "delayed"
        if ratio >= self.at_risk_slip_ratio:
            return "at_risk"
        return "on_track"

    def health(self, milestones: Sequence[Milestone]) -> Dict[str, object]:
        """Aggregate phase grades into a rollup."""
        grades = {m.id: self.grade(m) for m in milestones}
        counts: Dict[str, int] = {}
        for grade in grades.values():
            counts[grade] = counts.get(grade, 0) + 1

        done = sum(1 for m in milestones if m.complete)
        total = len(milestones)
        overall = "complete" if total and done == total else "in_progress"
        if not total:
            overall = "empty"
        elif counts.get("delayed"):
            overall = "delayed"
        elif counts.get("at_risk"):
            overall = "at_risk"

        return {
            "overall": overall,
            "milestones": total,
            "complete": done,
            "percent_complete": round((done / total * 100) if total else 0.0, 1),
            "grade_counts": counts,
            "grades": grades,
            "total_slip_days": round(sum(m.slip_days for m in milestones), 2),
        }

    def at_risk_ids(self, milestones: Sequence[Milestone]) -> List[str]:
        """Ids graded at_risk or delayed, worst slip first."""
        risky = [
            m for m in milestones if self.grade(m) in ("at_risk", "delayed")
        ]
        return [m.id for m in sorted(risky, key=lambda m: -m.slip_days)]
