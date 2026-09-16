---
id: TASK-20260916-002
title: Merge the repaired workflows into main and re-confirm the push gate
status: done
priority: high
created: 2026-09-16
updated: 2026-09-16
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [311]
blocked_by:
tokens: 0
---

# TASK-20260916-002 — Merge the repaired workflows into main

## Goal

The repaired workflow set existed only on a branch (`fig/workflows-sha-pin-repair`),
where it had twice been lost to workspace recycles. Make it durable on `main`, and
re-confirm — live, with the write grant active — whether the Fig App can now push
`.github/workflows/**` itself.

## Scope

- Verify the staged repair set against the repo's own verifier.
- Merge PR #311 so the set lives on `main`.
- Re-run the workflow push, and the discriminator that separates a permission
  refusal from a general push failure.

## Out of scope

- Installing the set into `.github/workflows/**` — that needs the App `workflows`
  permission, which is an installation setting, not something a push attempt can
  change.
- Reconciling the two staged kits (`workflows-repaired/` and the older
  `deliverables/ci/workflows-repaired/`); recorded as a note instead.

## Steps

- [x] Confirm `origin/main` state and the staging branch tip (`feeab8f`)
- [x] Validate the staged set: parse, `jobs:`, SHA pins
- [x] Merge PR #311 (squash → `9502acd`)
- [x] Confirm the merged files are byte-identical to the validated set
- [x] Re-run the workflow push with the grant active → still refused
- [x] Push a non-workflow file as the control → succeeds
- [x] Delete the probe branch

## Acceptance criteria

- [x] `workflows-repaired/` is present on `main` (13 files, +2448)
- [x] Merged workflow files byte-identical to the validated set (`diff -r` clean)
- [x] `verify_workflows.py` installed-tree run: PASS — 11 workflows parse, 28 refs pinned
- [x] Push control: non-workflow file succeeds; workflow file refused at transport

## Dependencies / blockers

Blocked on GitHub for the final install step: the App needs the `workflows`
permission granted **at the App installation** (Settings → GitHub Apps → fig-ai-agent
→ Permissions → Workflows: Read and write), not at the repository ruleset and not via
a write grant. Until then a maintainer installs the set with
`bash deliverables/ci/workflows-repaired/install.sh` (dry-run by default; `--apply`
writes).

## Files changed

| File | Change |
| --- | --- |
| `workflows-repaired/**` | Merged to `main` via PR #311 |
| `new.inprogress.done/done/TASK-20260916-002-workflow-repair-merge.md` | Added |
| `CHANGELOG.md` | Modified — records PR #311 |

## Validation

| Command | Result |
| --- | --- |
| `python deliverables/ci/verify_workflows.py --workflows workflows-repaired/.github/workflows --check-shas` | FAIL — 1 problem: `release_drafter.yaml` has no `jobs:` |
| `install.sh --apply` in a clean tree, then `verify_workflows.py --check-shas` | PASS — 11 workflows parse, 28 action refs SHA-pinned |
| `git push origin fig/workflows-apply-repair` | `! [remote rejected] … refusing to allow a GitHub App to create or update workflow` |
| `git push origin fig/push-probe` (non-workflow file) | `* [new branch]` — succeeded |

## Notes

- The root `workflows-repaired/` set authored by #311 keeps `release_drafter.yaml`
  in the set. It is a release-drafter *config*, not a workflow, so it must land as
  `.github/release-drafter.yml` (the app reads it from `.github/`), not inside
  `.github/workflows/`. The older kit already carries this mapping; the root set's
  README does not. Installing the root set as-is would leave one always-failing
  workflow — which is why the verified path is the `install.sh` kit.
- The push refusal is a real boundary, not a transient error: it reproduced on
  two separate attempts (grant absent, then grant approved) with identical wording,
  and the non-workflow control proves credentials and branch permissions are fine.

## Completion summary

PR #311 merged (`9502acd`); the repaired set is now durable on `main`. The live push
re-test reproduced the same transport-level refusal with the write grant active, and
the non-workflow control succeeded — settling cause as the App's `workflows`
permission scope, not repo rules. Installing the repaired tree into `.github/workflows/`
still requires a maintainer (one command) or the App permission being granted.
