---
title: "Agent Skill: Summary Reporter"
description: "Render an executive update from task state, leading with required decisions."
tags:
  - agents/communication
  - agents/reporting
  - agents/skills
doc_kind: "skill"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
---

# Summary Reporter

> Render an executive update from task state -- lead with what needs a decision, then status, then detail. Never buries a blocker.

**Module:** `knowledge.agents.summary_reporter.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/communication/reporting`

## Contract

`Summary Reporter` exposes one coordinator class. Renders a structured task list into an executive update that leads with what needs a human decision.

## Usage

```python
from knowledge.agents.summary_reporter.main import SummaryReporter, TaskState

md = SummaryReporter().report("Weekly update", [
    TaskState("T-1", "Ship auth", "done"),
    TaskState("T-2", "Wire billing", "blocked", blocker="waiting on keys"),
])
# Headline: "1 item(s) blocked; 0 decision(s) needed from you."
```

## Design notes

- The order is fixed: headline, decisions, blockers, status, detail. A
  reader who stops after the first line still knows what to do.
- The reporter is the only renderer in the suite; everything else returns
  machine-readable dicts, so this is the one place formatting lives.
- Detail rows are truncated with an explicit remainder count, never a
  silent cut.

## Tests

```bash
python -m pytest knowledge/agents/summary-reporter -q
```
