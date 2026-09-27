# Renumber map — TASK-20260916-006

The tracker integrity repair reassigned five IDs so every task ID is
unique. A number that used to mean one task must never silently mean
another, so the old -> new mapping is recorded here permanently.

| Old ID | New ID | File | Why it moved |
|---|---|---|---|
| `TASK-20260915-001` | `TASK-20260915-004` | `inprogress/TASK-20260915-001-dev-helpers-suite.md` | collided with done/TASK-20260915-001-fig-v4-docs |
| `TASK-20260915-001` | `TASK-20260915-005` | `inprogress/TASK-20260915-001-per-component-env-templates.md` | collided with done/TASK-20260915-001-fig-v4-docs |
| `TASK-20260916-001` | `TASK-20260916-005` | `inprogress/TASK-20260916-001-high-priority-fig-tasks.md` | collided with done/TASK-20260916-001-cross-repo-patch-suite |
| `TASK-20260916-003` | `TASK-20260916-006` | `new/TASK-20260916-003-tracker-integrity-repair.md` | collided with two done/ tasks |
| `TASK-20260916-003` | `TASK-20260916-007` | `done/TASK-20260916-003-chrome-devtools-mcp-setup.md` | collided with done/TASK-20260916-003-cache-scan-ci-gate (which kept the number) |
