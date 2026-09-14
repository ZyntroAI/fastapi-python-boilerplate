---
id: TASK-20260914-001
title: Documentation accuracy and repository hygiene
status: inprogress
priority: normal
created: 2026-09-14
updated: 2026-09-14
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [269, 271, 272, 273, 274, 275, 276, 277, 278, 279, 281, 282]
blocked_by:
tokens: 1246
---

# TASK-20260914-001 — Documentation accuracy and repository hygiene

## Goal

`README.md`, `LICENSE`, `package.json` and `PROBLEMS.md` describe the repository
as it actually is, and a script in the repository — not in an author's
workspace — is what keeps them honest.

## Scope

- Rewrite `README.md` so every claim is verifiable against `main`.
- Fill the `LICENSE` copyright holder; declare `license` in `package.json`.
- Repair `PROBLEMS.md`: stale counts, a duplicated problem id, a duplicated
  date section.
- Add `deliverables/docs-verify/` so documentation drift fails loudly.
- Record every merged PR in `CHANGELOG.md`.

## Out of scope

- Repairing the five unparseable workflows (P-001). Needs write access to
  `.github/workflows/`, which the automation App does not hold. Left as a known
  defect, and `docs-verify` reports it on every run so it cannot be forgotten.
- Removing `.env` from git and rotating its keys. A secret-rotation decision for
  the owner, not an autonomous change.
- Pruning the stale `zyntromedia-*` branches. Destructive; owner's call.
- Changing any application code under `app/`, `tests/` or the config. Every PR
  in this task touched documentation or added one new deliverable.

## Steps

- [x] Measure the tree: workflows, deliverables, docs, root entries, action pins
- [x] Rewrite `README.md` grounded in those measurements (PR #269)
- [x] Correct the counts that drifted from concurrent merges (PRs #272, #273)
- [x] Fill the `LICENSE` holder — `Zyntro Media` (PR #274)
- [x] Declare `"license": "MIT"` in `package.json` (PR #276)
- [x] Repair `PROBLEMS.md`: P-002 count, duplicate P-009, duplicate date (PR #278)
- [x] Add `deliverables/docs-verify/` with tests (PR #281)
- [x] Record each merge in `CHANGELOG.md` (PRs #271, #275, #277, #279, #282)

## Acceptance criteria

- [x] `README.md` describes `main` — 16/17 `docs-verify` checks pass on `main`;
      the single failure is the known P-001 defect, not a README error.
- [x] `LICENSE` names a real holder and contains no placeholder brackets.
- [x] `package.json` parses and declares `license: MIT`.
- [x] `PROBLEMS.md` has unique problem ids (`P-001`…`P-011`), one section per
      date, and dates in descending order.
- [x] `deliverables/docs-verify/` ships with a passing suite (17 tests).
- [x] Every PR merged by this task appears in `CHANGELOG.md`.
- [x] `python3 -m pytest tests/` inside `new.inprogress.done/` still passes.

## Dependencies / blockers

None for what is in scope. The out-of-scope items are blocked on owner decisions
or on `.github/workflows/` write access, and are recorded in `PROBLEMS.md`
rather than here.

## Files changed

| File | Change |
| --- | --- |
| `README.md` | Rewritten against the live tree; counts corrected twice |
| `LICENSE` | Placeholder holder filled in |
| `package.json` | `license` field added |
| `PROBLEMS.md` | Stale count fixed; duplicate id and date section repaired |
| `CHANGELOG.md` | Entries for PRs #269, #274, #276, #278, #281 |
| `deliverables/docs-verify/` | Added — engine, CLI, SKILL.yaml, README, 17 tests |
| `deliverables/README.md` | Index row for the new deliverable |

## Validation

| Command | Result |
| --- | --- |
| `python deliverables/docs-verify/scripts/verify_docs.py` (on `main`) | 16/17 passed, 1 failed — the failure is P-001, the five unparseable workflows |
| `python -m pytest deliverables/docs-verify/tests/ -q` | 17 passed |
| `python -m pytest tests/` (in `new.inprogress.done/`) | 20 passed |
| `python -c "import json; json.load(open('package.json'))['license']"` | `MIT` |
| `grep -c "^### P-" PROBLEMS.md` | 11 entries, no id duplicated |
| `gh pr view 281 --json state` | `MERGED` |

## Token usage

Estimated with `len(text) // 4` over the files above: **1246**. This is a size
proxy, not a measured API figure.

## Notes

Two of the count corrections (#272, #273) were caused by a concurrent merge
landing while the fix was in flight, and a third (inside #281) by the same
cause again. That repetition is the reason `docs-verify` compares counts against
what the README declares rather than against a frozen number: a hand-fix does
not survive the next merge, and a check that reads the declaration does.

`docs-verify` is deliberately listed as failing on `main` in one check. That is
P-001 surfacing on every run — the point of the tool, not a defect in it.

## Completion summary

Not yet moved to `done/`. Steps and acceptance criteria are all met and every PR
is merged, so the move is a formality pending the owner's call on whether the
out-of-scope items (P-001 workflow repair, `.env` rotation, branch pruning)
should be folded in or split into their own tasks.
