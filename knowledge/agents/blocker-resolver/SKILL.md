---
title: "Agent Skill: Blocker Resolver"
description: "Classify obstacles, attach a resolution playbook, and route escalations."
tags:
  - agents/execution
  - agents/recovery
  - agents/skills
doc_kind: "skill"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
---

# Blocker Resolver

> Classify obstacles, attach the matching resolution playbook, and decide which ones need a human escalation before work can resume.

**Module:** `knowledge.agents.blocker_resolver.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/execution/recovery`

## Contract

`Blocker Resolver` exposes one coordinator class. Classifies an obstacle against a fixed playbook and decides whether it can be cleared locally or needs a human.

## Usage

```python
from knowledge.agents.blocker_resolver.main import Blocker, BlockerResolver

out = BlockerResolver().triage([
    Blocker("b1", "missing lib", "dependency"),
    Blocker("b2", "no workflows scope", "permission", waiting_on="repo admin"),
])
# {"self_resolvable": 1, "escalation_ids": ["b2"]}
```

## Design notes

- Permission and unclear-requirement blockers always escalate; a machine
  cannot grant itself a scope or invent a requirement.
- Any blocker escalates once its retry budget is spent, so a loop can
  never spin indefinitely on a problem it cannot solve.
- An unrecognised category raises rather than guessing a playbook.

## Tests

```bash
python -m pytest knowledge/agents/blocker-resolver -q
```
