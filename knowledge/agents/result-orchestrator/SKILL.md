---
title: "Agent Skill: Result Orchestrator"
description: "Collect subtask outcomes, apply quality gates, and reduce them to one verdict."
tags:
  - agents/execution
  - agents/orchestration
  - agents/skills
doc_kind: "skill"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
---

# Result Orchestrator

> Collect subtask outcomes, apply quality gates, and reduce them to a single verdict. A subtask only counts as passing when it succeeded AND cleared every gate.

**Module:** `knowledge.agents.result_orchestrator.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/execution/orchestration`

## Contract

`Result Orchestrator` exposes one coordinator class. Reduces many subtask outcomes into a single verdict. A subtask counts as passing only when it succeeded **and** every quality gate passed.

## Usage

```python
from knowledge.agents.result_orchestrator.main import (
    GateResult, ResultOrchestrator, SubtaskResult)

out = ResultOrchestrator(min_pass_ratio=0.8).aggregate([
    SubtaskResult("api", True, [GateResult("tests", True)]),
    SubtaskResult("ui", True, [GateResult("lint", False, "3 errors")]),
])
# {"verdict": "failed", "failure_reasons": {"ui": "quality gate failed: lint"}}
```

## Design notes

- A failed gate is named in `failure_reasons`; a raw error is preserved
  ahead of gate detail, because it is the more actionable signal.
- An empty input is `empty`, never `passed` -- silence is not success.
- `blocked_by()` returns the ids that must be fixed before the job can pass.

## Tests

```bash
python -m pytest knowledge/agents/result-orchestrator -q
```
