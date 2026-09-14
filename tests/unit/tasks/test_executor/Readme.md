ได้ครับ ไฟล์นี้ควรทดสอบ execution lifecycle ตั้งแต่ resolved skills → execution → events → result → artifact/memory → failure/retry → budget guard เพื่อให้ Live Task ทำงานแบบ deterministic และไม่ยิง AI เกินงบโดยไม่จำเป็น

tests/unit/tasks/test_executor.py

python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

# ============================================================
# Test doubles
# ============================================================

@dataclass
class FakeSkill:
    id: str
    version: str = "1.0.0"

@dataclass
class FakeRequirement:
    requirement: str = "Create a login form"
    mode: str = "live"
    mock_mode: bool = False

    max_cost_usd: float | None = None
    max_output_tokens: int | None = None

    save_artifact: bool = False
    save_memory: bool = False

@dataclass
class FakeExecutionEvent:
    type: str
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class FakeExecutionResult:
    task_id: str
    status: str
    output: str = ""
    events: list[FakeExecutionEvent] = field(default_factory=list)

    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0

    artifact_id: str | None = None
    memory_id: str | None = None

class FakeProvider:
    def __init__(
        self,
        *,
        response: str = "Generated result",
        cost_usd: float = 0.01,
        input_tokens: int = 100,
        output_tokens: int = 200,
        fail: bool = False,
    ) -> None:
        self.response = response
        self.cost_usd = cost_usd
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.fail = fail

        self.calls = 0

    def generate(
        self,
        requirement: FakeRequirement,
        skills: list[FakeSkill],
    ) -> dict[str, Any]:
        self.calls += 1

        if self.fail:
            raise RuntimeError("provider failure")

        return {
            "output": self.response,
            "cost_usd": self.cost_usd,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

class FakeCache:
    def __init__(
        self,
        result: dict[str, Any] | None = None,
    ) -> None:
        self.result = result
        self.lookups = 0

    def get(self, requirement: FakeRequirement) -> dict[str, Any] | None:
        self.lookups += 1
        return self.result

class FakeArtifactStore:
    def __init__(self) -> None:
        self.saved: list[dict[str, Any]] = []

    def save(
        self,
        *,
        task_id: str,
        output: str,
    ) -> str:
        artifact_id = f"artifact-{len(self.saved) + 1}"

        self.saved.append(
            {
                "id": artifact_id,
                "task_id": task_id,
                "output": output,
            }
        )

        return artifact_id

class FakeMemoryStore:
    def __init__(self) -> None:
        self.saved: list[dict[str, Any]] = []

    def save(
        self,
        *,
        task_id: str,
        content: str,
    ) -> str:
        memory_id = f"memory-{len(self.saved) + 1}"

        self.saved.append(
            {
                "id": memory_id,
                "task_id": task_id,
                "content": content,
            }
        )

        return memory_id

class FakeBudgetGuard:
    def __init__(self) -> None:
        self.checks: list[float] = []

    def check(
        self,
        estimated_cost_usd: float,
        max_cost_usd: float | None,
    ) -> None:
        self.checks.append(estimated_cost_usd)

        if (
            max_cost_usd is not None
            and estimated_cost_usd > max_cost_usd
        ):
            raise BudgetExceededError(
                "task budget exceeded"
            )

class BudgetExceededError(RuntimeError):
    pass

class FakeExecutor:
    """
    Minimal executor contract.

    Replace this test double with:
        from core.tasks.executor import TaskExecutor

    once the production executor is implemented.
    """

    def __init__(
        self,
        provider: FakeProvider,
        cache: FakeCache | None = None,
        artifact_store: FakeArtifactStore | None = None,
        memory_store: FakeMemoryStore | None = None,
        budget_guard: FakeBudgetGuard | None = None,
        max_retries: int = 3,
    ) -> None:
        self.provider = provider
        self.cache = cache or FakeCache()
        self.artifact_store = (
            artifact_store or FakeArtifactStore()
        )
        self.memory_store = (
            memory_store or FakeMemoryStore()
        )
        self.budget_guard = (
            budget_guard or FakeBudgetGuard()
        )
        self.max_retries = max_retries

    def execute(
        self,
        *,
        task_id: str,
        requirement: FakeRequirement,
        skills: list[FakeSkill],
    ) -> FakeExecutionResult:
        events = [
            FakeExecutionEvent("received"),
            FakeExecutionEvent("executing"),
        ]

        cached = self.cache.get(requirement)

        if cached is not None:
            events.append(
                FakeExecutionEvent("cache_hit")
            )

            output = cached["output"]
           


รัน

bash
pytest tests/unit/tasks/test_executor.py -v


หรือรัน parser + resolver + executor:

bash
pytest tests/unit/tasks/test_parser.py \
       tests/unit/tasks/test_resolver.py \
       tests/unit/tasks/test_executor.py \
       -v


Contract ที่ core/tasks/executor.py ควรมี

text
TaskExecutor
│
├── budget_guard
├── cache
├── provider_router
├── artifact_store
├── memory_store
├── event_sink
└── retry_policy


execution order ควรล็อกไว้เป็น:

text
validate
   ↓
bud










