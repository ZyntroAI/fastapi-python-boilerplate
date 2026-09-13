"""Task Master -- goal decomposition and dependency ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class DependencyCycleError(ValueError):
    """Raised when subtasks declare a circular dependency."""


@dataclass
class Subtask:
    """One atomic unit of work."""

    id: str
    title: str
    depends_on: List[str] = field(default_factory=list)
    estimate_hours: float = 1.0

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("subtask id is required")
        if self.estimate_hours <= 0:
            raise ValueError(f"{self.id}: estimate_hours must be positive")


class TaskMaster:
    """Decompose a goal and order the parts.

    Args:
        max_parallel: Upper bound on subtasks reported as simultaneously ready.
    """

    def __init__(self, max_parallel: int = 4) -> None:
        if max_parallel < 1:
            raise ValueError("max_parallel must be >= 1")
        self.max_parallel = max_parallel

    def validate(self, subtasks: Sequence[Subtask]) -> None:
        """Check ids are unique and every dependency resolves to a known subtask."""
        seen: Dict[str, bool] = {}
        for task in subtasks:
            if task.id in seen:
                raise ValueError(f"duplicate subtask id: {task.id}")
            seen[task.id] = True
        for task in subtasks:
            for dep in task.depends_on:
                if dep not in seen:
                    raise ValueError(f"{task.id} depends on unknown subtask {dep}")

    def execution_order(self, subtasks: Sequence[Subtask]) -> List[List[str]]:
        """Group subtasks into waves; every task in a wave is dependency-free.

        Returns a list of waves, each a sorted list of subtask ids. Raises
        ``DependencyCycleError`` if no valid ordering exists.
        """
        self.validate(subtasks)
        remaining = {t.id: set(t.depends_on) for t in subtasks}
        waves: List[List[str]] = []
        placed: set[str] = set()

        while remaining:
            ready = sorted(
                tid for tid, deps in remaining.items() if deps <= placed
            )
            if not ready:
                blocked = sorted(remaining)
                raise DependencyCycleError(
                    "circular dependency among: " + ", ".join(blocked)
                )
            waves.append(ready)
            placed.update(ready)
            for tid in ready:
                del remaining[tid]
        return waves

    def critical_path_hours(self, subtasks: Sequence[Subtask]) -> float:
        """Longest dependency chain by estimate -- the floor on wall-clock time."""
        self.validate(subtasks)
        by_id = {t.id: t for t in subtasks}
        memo: Dict[str, float] = {}

        def depth(tid: str) -> float:
            if tid in memo:
                return memo[tid]
            task = by_id[tid]
            best = 0.0
            for dep in task.depends_on:
                best = max(best, depth(dep))
            memo[tid] = best + task.estimate_hours
            return memo[tid]

        return round(max((depth(t.id) for t in subtasks), default=0.0), 2)

    def plan(self, goal: str, subtasks: Sequence[Subtask]) -> Dict[str, object]:
        """Render the full plan as a machine-readable dict."""
        waves = self.execution_order(subtasks)
        return {
            "goal": goal,
            "subtask_count": len(subtasks),
            "waves": waves,
            "wave_count": len(waves),
            "parallel_width": max((len(w) for w in waves), default=0),
            "critical_path_hours": self.critical_path_hours(subtasks),
            "max_parallel": self.max_parallel,
        }
