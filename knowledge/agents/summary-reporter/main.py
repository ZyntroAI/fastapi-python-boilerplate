"""Summary Reporter -- executive updates from structured task state."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class TaskState:
    """Flattened state for one work item."""

    id: str
    title: str
    status: str
    blocker: str = ""
    needs_decision: str = ""

    def __post_init__(self) -> None:
        if self.status not in ("done", "in_progress", "blocked", "not_started"):
            raise ValueError(f"{self.id}: unknown status {self.status!r}")


class SummaryReporter:
    """Build an executive summary that leads with what needs a human.

    Args:
        max_detail_items: Rows of raw detail to include.
    """

    def __init__(self, max_detail_items: int = 10) -> None:
        self.max_detail_items = max_detail_items

    def counts(self, tasks: Sequence[TaskState]) -> Dict[str, int]:
        out = {"done": 0, "in_progress": 0, "blocked": 0, "not_started": 0}
        for t in tasks:
            out[t.status] += 1
        return out

    def decisions_needed(self, tasks: Sequence[TaskState]) -> List[Dict[str, str]]:
        """Every item waiting on a human, most blocked first."""
        waiting = [
            {"id": t.id, "title": t.title, "ask": t.needs_decision}
            for t in tasks
            if t.needs_decision.strip()
        ]
        return waiting

    def headline(self, tasks: Sequence[TaskState]) -> str:
        """One line an executive can read on its own."""
        if not tasks:
            return "No work in flight."
        c = self.counts(tasks)
        decisions = len(self.decisions_needed(tasks))
        if c["blocked"]:
            return (
                f"{c['blocked']} item(s) blocked; "
                f"{decisions} decision(s) needed from you."
            )
        if decisions:
            return f"On track; {decisions} decision(s) needed from you."
        if c["done"] == len(tasks):
            return "All items complete."
        return f"On track; {c['in_progress']} item(s) in progress."

    def report(self, title: str, tasks: Sequence[TaskState]) -> str:
        """Render the full markdown update."""
        lines = [f"# {title}", "", self.headline(tasks), ""]

        decisions = self.decisions_needed(tasks)
        if decisions:
            lines += ["## Needs your decision", ""]
            for d in decisions:
                lines.append(f"- **{d['id']}** -- {d['ask']} ({d['title']})")
            lines.append("")

        blocked = [t for t in tasks if t.status == "blocked"]
        if blocked:
            lines += ["## Blocked", ""]
            for t in blocked:
                reason = t.blocker or "reason not recorded"
                lines.append(f"- **{t.id}** -- {t.title}: {reason}")
            lines.append("")

        c = self.counts(tasks)
        lines += [
            "## Status",
            "",
            f"- Done: {c['done']}",
            f"- In progress: {c['in_progress']}",
            f"- Blocked: {c['blocked']}",
            f"- Not started: {c['not_started']}",
            "",
        ]

        detail = tasks[: self.max_detail_items]
        lines += ["## Detail", ""]
        for t in detail:
            lines.append(f"- {t.id} -- {t.title} [{t.status}]")
        if len(tasks) > len(detail):
            lines.append(f"- ...and {len(tasks) - len(detail)} more")
        return "\n".join(lines)
