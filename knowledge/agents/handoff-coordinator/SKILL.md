# Handoff Coordinator

> Validate a handoff payload before work passes to another team. Rejects an incomplete handoff rather than letting it across the gap.

**Module:** `knowledge.agents.handoff_coordinator.main` &middot; **Version:** 1.0.0 &middot; **Type:** `agents/coordination/handoff`

## Contract

`Handoff Coordinator` exposes one coordinator class. Validates that a handoff carries everything the receiver needs before it crosses an owner boundary.

## Usage

```python
from knowledge.agents.handoff_coordinator.main import Handoff, HandoffCoordinator

receipt = HandoffCoordinator().receipt(Handoff(
    work_id="W-1", from_owner="backend", to_owner="frontend",
    summary="API contract finalized", artifacts=["openapi.json"],
    acceptance_criteria=["returns 200 on /health"],
    next_action="wire the client to /health",
))
# {"status": "accepted", "receiver_next_step": "wire the client to /health"}
```

## Design notes

- Four fields are mandatory: summary, artifacts, acceptance_criteria,
  next_action. A handoff missing any of them is rejected, not trimmed.
- Handing off to yourself is rejected -- it is a state change, not a handoff.
- `require_open_questions=True` blocks a handoff carrying unresolved questions.

## Tests

```bash
python -m pytest knowledge/agents/handoff-coordinator -q
```
