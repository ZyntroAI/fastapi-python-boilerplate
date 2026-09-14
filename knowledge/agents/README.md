# Agent Task Skills

Six composable skills for managing a unit of work end to end -- plan it, run it,
grade it, unblock it, hand it over, and report on it.

They are deliberately small and dependency-free: pure Python, no network, no
state on disk. Each is a module with a dataclass vocabulary and one coordinator
class, so they compose in any pipeline and are trivial to unit test.

## Skills

| Skill | Responsibility | Entry point |
|---|---|---|
| [task-master](task-master/SKILL.md) | Decompose a goal, order by dependency, refuse cycles | `TaskMaster.plan()` |
| [result-orchestrator](result-orchestrator/SKILL.md) | Collect outcomes, apply quality gates, reduce to a verdict | `ResultOrchestrator.aggregate()` |
| [milestone-tracker](milestone-tracker/SKILL.md) | Grade timeline health from slip against schedule | `MilestoneTracker.health()` |
| [blocker-resolver](blocker-resolver/SKILL.md) | Classify obstacles and route escalations | `BlockerResolver.triage()` |
| [handoff-coordinator](handoff-coordinator/SKILL.md) | Gate a handoff on completeness | `HandoffCoordinator.receipt()` |
| [summary-reporter](summary-reporter/SKILL.md) | Render an executive update | `SummaryReporter.report()` |

## Lifecycle

```
goal --[task-master]--> waves
waves --[result-orchestrator]--> verdict + failure_reasons
verdict --[milestone-tracker]--> timeline health
health --[blocker-resolver]--> resolutions + escalations
work --[handoff-coordinator]--> accepted | rejected
all --[summary-reporter]--> executive update
```

## Design rules

- **Deterministic.** Same input, same output -- no clocks, no randomness.
- **Explicit failure.** A cycle, an unknown dependency, an unknown status, or an
  incomplete handoff raises or is rejected; nothing is silently tolerated.
- **No hidden state.** Every skill is a plain class; construct it, call it, drop it.
- **Machine-first.** Coordinators return dicts; the reporter is the only renderer.

## Running the tests

```bash
python -m pytest knowledge/agents -q
```
