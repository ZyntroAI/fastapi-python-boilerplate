---
id: TASK-20260916-006
title: Repair the task tracker's own integrity failures and stop id collisions at the source
status: new
priority: high
created: 2026-09-16
updated: 2026-09-26
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by:
tokens: 0
---

# TASK-20260916-006 — Repair the task tracker's own integrity failures

## Goal

`python3 -m pytest tests/ -q` inside `new.inprogress.done/` passes on `main`. It
does not today: two of its twenty checks fail, so the tracker that enforces the
Definition of Done does not itself satisfy it.

## Scope

Two failing checks, and the mechanism that produced them.

- **`test_ids_unique` — id `TASK-20260915-001` is used twice on `main`.** Once by
  `done/TASK-20260915-001-fig-v4-docs.md`, once by
  `inprogress/TASK-20260915-001-per-component-env-templates.md`. A third file on
  the open `fig/dev-helpers-suite-v2` branch (PR #310) carries the same id.
- **`test_done_tasks_have_evidence` — `done/TASK-20260915-001-fig-v4-docs.md` has
  `prs: []`.** A task moved to `done/` without any PR reference, which is exactly
  what that check exists to catch.
- **The collision is not a one-off.** `TASK-20260916-001` is likewise claimed
  twice — by `done/TASK-20260916-001-cross-repo-patch-suite.md` on `main` and by
  `inprogress/TASK-20260916-001-high-priority-fig-tasks.md` on the open
  `fig/high-fixes-vite-lint` branch (PR #303). Independently authored
  workstreams each reached for the same date sequence, which means the next one
  will too.
- **`tools/tasks.py new` allocates the next id by looking at existing files, but
  nothing refuses a hand-written file that reuses one** — and the test suite is
  the only thing that notices, after the fact.

## Out of scope

- Rewriting git history to de-duplicate ids retroactively. The collisions are
  resolved by renumbering the files that are still open, not by rewriting what
  has shipped.
- The `docs-verify` gate and the CHANGELOG side of the Definition of Done. Those
  are separate mechanisms; this task is the tracker's own consistency only.
- The open PRs themselves (#303, #310). Their task files need renumbering, but
  that edit belongs on their branches, not here.

## Steps

- [ ] Reproduce: run `python3 -m pytest tests/ -q` in `new.inprogress.done/` and
      capture the two failures verbatim.
- [ ] Renumber the duplicate that is still open. `TASK-20260915-001` stays with
      the `done/` task (it shipped); `inprogress/TASK-20260915-001-per-component-env-templates.md`
      moves to the next free id and is renamed to match.
- [ ] Give `done/TASK-20260915-001-fig-v4-docs.md` the PR evidence it is missing,
      or move it back to `inprogress/` if no PR exists — `done` without evidence
      is not a status, it is a claim.
- [ ] Make `tools/tasks.py new` refuse to allocate an id already in use, so the
      next hand-written collision fails at creation instead of at test time.
- [ ] Add a test for that refusal, alongside the existing `test_new_creates_file_in_new`.
- [ ] Note the renumbering the two open PR branches still need, in each task's
      own file, so the fix is not lost when those branches merge.

## Acceptance criteria

- [ ] `python3 -m pytest tests/ -q` in `new.inprogress.done/` reports **20 passed**,
      with no failures.
- [ ] No id appears twice across `new/`, `inprogress/`, `done/`, and `archive/`.
- [ ] `tools/tasks.py new "test"` against an id already present exits non-zero and
      writes no file.
- [ ] Every file in `done/` has a non-empty `prs:`.
- [ ] Existing tests still pass.

## Dependencies / blockers

None. Both defects are reproducible on `main` today from a clean clone.

## Files changed

| File | Change |
| --- | --- |
| `new.inprogress.done/new/TASK-20260916-006-tracker-integrity-repair.md` | Added |
| `new.inprogress.done/inprogress/TASK-20260915-001-per-component-env-templates.md` | Renamed / renumbered (not yet done) |
| `new.inprogress.done/done/TASK-20260915-001-fig-v4-docs.md` | PR evidence added, or moved back to `inprogress/` (not yet done) |
| `new.inprogress.done/tools/tasks.py` | Duplicate-id refusal (not yet done) |
| `new.inprogress.done/tests/test_tasks.py` | Test for the refusal (not yet done) |

## Validation

| Command | Result |
| --- | --- |
| `git clone --depth 1` then `cd new.inprogress.done && python3 -m pytest tests/ -q` | **FAIL** — `2 failed, 18 passed` |
| ↳ `test_ids_unique` | `AssertionError: id ซ้ำ: ['TASK-20260915-001']` |
| ↳ `test_done_tasks_have_evidence` | `AssertionError: TASK-20260915-001-fig-v4-docs.md: อยู่ใน done/ แต่ไม่มี PR อ้างอิง` |

Reproduced against `main` at `2f2a234` (2026-09-16), from a clean clone.

## Token usage

Estimated with `len(text) // 4` over the files above: **0**. This is a size
proxy, not a measured API figure.

## Notes

The tracker's rule is that status lives in the folder, and
`tests/test_tasks.py` is what holds the two in agreement. That check is doing its
job — it caught both defects. What is missing is anything that catches them
*before* the file lands, which is why `tools/tasks.py` is in scope here: the
allocation side should refuse a duplicate the same way the test side reports one.

`test_ids_unique` and `test_done_tasks_have_evidence` fail on `main` as of
2026-09-16, so this is a live defect and not a hypothetical hardening pass.

The two open PR branches need their task files renumbered independently:
`fig/high-fixes-vite-lint` (#303) holds `TASK-20260916-001-high-priority-fig-tasks.md`,
and `fig/dev-helpers-suite-v2` (#310) holds `TASK-20260915-001-dev-helpers-suite.md`.
Those branches predate this task; renumbering them on their own branches keeps
each PR self-contained.

## Completion summary

Not yet complete. Fill in when moving to `done/`.
