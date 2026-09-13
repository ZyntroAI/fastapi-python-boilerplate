---
title: "Agent Skill: Milestone Tracker"
description: "Grade phase timeline health from slip against schedule and burn."
tags:
  - agents/planning
  - agents/tracking
  - agents/skills
doc_kind: "skill"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
---

# Milestone Tracker

> Track phases against a plan and grade timeline health from slip against schedule and elapsed-time burn.

**Module:** `knowledge.agents.milestone_tracker.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/planning/tracking`

## Contract

`Milestone Tracker` exposes one coordinator class. Grades each phase of a plan from slip against its schedule, then rolls the grades up into one health verdict.

## Usage

```python
from knowledge.agents.milestone_tracker.main import Milestone, MilestoneTracker

health = MilestoneTracker().health([
    Milestone("m1", "Schema", planned_days=10, actual_days=10, complete=True),
    Milestone("m2", "API", planned_days=10, actual_days=15),
])
# {"overall": "delayed", "percent_complete": 50.0, "total_slip_days": 5.0}
```

## Design notes

- Grades are `complete | delayed | at_risk | on_track`; the overall
  rollup takes the worst of them, so one slipping phase is never averaged away.
- Thresholds are configurable but validated -- at-risk must sit below delayed.

## Tests

```bash
python -m pytest knowledge/agents/milestone-tracker -q
```
