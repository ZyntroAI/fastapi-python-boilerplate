---
id: TASK-20260915-001
title: Dev-helpers suite for GitHub automation friction
status: inprogress
priority: normal
created: 2026-09-15
updated: 2026-09-15
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [285]
blocked_by:
tokens: 4412
---

# TASK-20260915-001 — Dev-helpers suite for GitHub automation friction

## Goal

Four friction points in automated GitHub work are decided *before* the work is
done rather than discovered after it fails: whether a push will be accepted,
whether a workflow parses, whether an action is pinned, and whether a PR body
actually satisfies the Definition of Done.

## Scope

- Add `deliverables/dev-helpers/` — four stdlib-only modules, no dependencies.
- Tests for every promised behaviour (25 tests, stdlib `unittest`).
- Thai and English guides documenting problem → mechanism → usage → gotchas.
- Wire it into `CHANGELOG.md`, `deliverables/README.md` and `docs/README.md`.

## Out of scope

- **Calling the GitHub API.** `perm_checker` takes the permission map as input
  rather than reading it live, so the suite runs in a sandbox with no token.
  Reading permissions directly would make it untestable offline.
- **Pushing or opening PRs on its own.** The suite is a decision layer; the code
  that acts on its verdict stays outside.
- **Repairing the repo's existing unpinned actions.** `ci_workflow` reports them;
  changing `.github/workflows/` needs the `workflows` scope the App does not
  hold. Same known defect as P-001, same reason.

## Steps

- [x] Clone `main`, confirm the `deliverables/` convention from an existing suite
- [x] `perm_checker.py` — permission decision from changed paths
- [x] `ci_workflow.py` — pin audit and parse state
- [x] `approval_doc.py` — grantable permission request
- [x] `pr_helper.py` — PR body with visible DoD gaps
- [x] Tests for all four; run to green
- [x] `README.md`, `SKILL.md`, `manifest.json`, `GUIDE.md`, `GUIDE.en.md`
- [x] `CHANGELOG.md`, `deliverables/README.md`, `docs/README.md`
- [x] Commit, patch, verify against a fresh clone of `main`
- [x] Push branch and open PR (#285)

## Acceptance criteria

- [x] `python3 -m unittest discover -s dev_helpers/tests -t .` — 25 passed.
- [x] Each of the four tools imports and runs with no third-party package.
- [x] The patch applies to a fresh clone of `main` (`git apply --check` clean)
      and the tests pass **after** applying, not only in the source tree.
- [x] `check_push` blocks a change set containing one workflow file and reports
      the whole push blocked, not just that file.
- [x] `checklist` leaves an unmentioned DoD item unchecked.
- [x] `CHANGELOG.md` has an entry for this work.

## Dependencies / blockers

None for what is in scope. This change set touches no `.github/workflows/` file,
so it does not need the `workflows` scope — verified before pushing.

## Files changed

| File | Change |
| --- | --- |
| `deliverables/dev-helpers/dev_helpers/perm_checker.py` | Added |
| `deliverables/dev-helpers/dev_helpers/ci_workflow.py` | Added |
| `deliverables/dev-helpers/dev_helpers/approval_doc.py` | Added |
| `deliverables/dev-helpers/dev_helpers/pr_helper.py` | Added |
| `deliverables/dev-helpers/dev_helpers/__init__.py` | Added — flat re-exports |
| `deliverables/dev-helpers/dev_helpers/tests/test_dev_helpers.py` | Added — 25 tests |
| `deliverables/dev-helpers/README.md` | Added |
| `deliverables/dev-helpers/SKILL.md` | Added — spec and promised behaviours |
| `deliverables/dev-helpers/manifest.json` | Added |
| `deliverables/dev-helpers/GUIDE.md` | Added — Thai guide |
| `deliverables/dev-helpers/GUIDE.en.md` | Added — English guide |
| `CHANGELOG.md` | Entry for 2026-09-15 |
| `deliverables/README.md` | Index row |
| `docs/README.md` | Index row |

## Validation

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s dev_helpers/tests -t . -v` | 25 passed |
| `git apply --check dev-helpers-suite.patch` (fresh clone of `main`) | clean |
| `python3 -m unittest ...` after applying the patch | 25 passed |
| `gh pr view 285 --json mergeable` | `MERGEABLE`, 15 files |

## Token usage

Estimated with `len(text) // 4` over the files above: **4412**. This is a size
proxy, not a measured API figure.

## Notes

`normalize_path` exists because the obvious implementation is wrong in a way
that fails *silently*. `str.lstrip("./")` takes a set of characters, not a
prefix, so it strips the leading dot from `.github/` and the subsequent
`startswith(".github/workflows/")` test never matches — a blocked push would be
reported as a pass. The suite carries a test asserting that `lstrip` gives the
wrong answer, so the shortcut cannot quietly come back.

`parse_state` reports which engine decided (`pyyaml` or `structural`). The
structural fallback is deliberately lenient and must never be read as a thorough
check; naming the engine in the output is what keeps that honest.

## Completion summary

Not yet moved to `done/`. PR #285 is open and unmerged; the move to `done/`
follows the merge, per the repository's convention.
