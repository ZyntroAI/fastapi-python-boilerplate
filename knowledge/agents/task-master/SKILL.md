---
title: "Agent Skill: Task Master"
description: "Decompose a goal into atomic subtasks, order by dependency, and refuse cycles."
tags:
  - agents/planning
  - agents/decomposition
  - agents/skills
doc_kind: "skill"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
---

# Task Master

> Break a goal into atomic subtasks, resolve dependencies, and emit a deterministic execution order. Refuses to schedule a plan containing a dependency cycle.

**Module:** `knowledge.agents.task_master.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/planning/decomposition`

## Contract

`Task Master` exposes one coordinator class. Decomposes a goal into atomic subtasks and returns a wave-ordered execution plan. A wave contains only subtasks whose dependencies are already satisfied, so every wave can run fully in parallel.

## Usage

```python
from knowledge.agents.task_master.main import Subtask, TaskMaster

plan = TaskMaster().plan("Ship the feature", [
    Subtask("design", "Design schema", estimate_hours=3),
    Subtask("api", "Build API", depends_on=["design"], estimate_hours=5),
    Subtask("ship", "Ship", depends_on=["api"], estimate_hours=1),
])
# {"waves": [["design"], ["api"], ["ship"]], "critical_path_hours": 9.0, ...}
```

## Design notes

- A circular dependency raises `DependencyCycleError` -- the plan is
  never emitted in a state that cannot be executed.
- `critical_path_hours` is the longest dependency chain, which is the
  floor on wall-clock time regardless of available parallelism.

## Tests

```bash
python -m pytest knowledge/agents/task-master -q
```
