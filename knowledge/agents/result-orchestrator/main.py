"""Result Orchestrator -- outcome aggregation and quality gates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


@dataclass
class GateResult:
    """One quality gate applied to a subtask result."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class SubtaskResult:
    """The outcome of one subtask."""

    id: str
    ok: bool
    gates: List[GateResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        """True only when the task succeeded and every gate passed."""
        return self.ok and all(g.passed for g in self.gates)

    def failed_gates(self) -> List[str]:
        return [g.name for g in self.gates if not g.passed]


class ResultOrchestrator:
    """Reduce many subtask results into one verdict.

    Args:
        min_pass_ratio: Fraction of subtasks that must pass to report success.
    """

    def __init__(self, min_pass_ratio: float = 1.0) -> None:
        if not 0.0 <= min_pass_ratio <= 1.0:
            raise ValueError("min_pass_ratio must be between 0 and 1")
        self.min_pass_ratio = min_pass_ratio

    def aggregate(self, results: Sequence[SubtaskResult]) -> Dict[str, object]:
        """Reduce results to a verdict dict with per-task reasons."""
        total = len(results)
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        reasons: Dict[str, str] = {}
        for r in failed:
            if not r.ok:
                reasons[r.id] = r.error or "subtask reported failure"
            else:
                reasons[r.id] = "quality gate failed: " + ", ".join(r.failed_gates())

        ratio = (len(passed) / total) if total else 1.0
        if total == 0:
            verdict = "empty"
        elif not failed:
            verdict = "passed"
        elif ratio >= self.min_pass_ratio:
            verdict = "passed_with_warnings"
        else:
            verdict = "failed"

        return {
            "verdict": verdict,
            "total": total,
            "passed": len(passed),
            "failed": len(failed),
            "pass_ratio": round(ratio, 4),
            "failure_reasons": reasons,
        }

    def blocked_by(self, results: Sequence[SubtaskResult]) -> List[str]:
        """Ids of subtasks that must be fixed before the whole job can pass."""
        return sorted(r.id for r in results if not r.passed)
