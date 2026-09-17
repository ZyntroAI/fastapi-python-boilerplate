---
id: TASK-20260916-004
title: Install repaired workflows — handoff PR (App lacks workflows permission)
status: done
priority: high
created: 2026-09-16
updated: 2026-09-16
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by: GitHub App `fig-ai-agent` missing `workflows` permission (installation setting)
tokens: 0
---

# TASK-20260916-004 — Install repaired workflows (handoff)

## Goal

Land the repaired workflow set on `main` so CI stops failing, after the request
"fix what's blocking PR #316, then merge it."

## What the request turned out to be

**PR #316 was already merged** (squash `de5648a`, 2026-09-16T14:20Z); all eight of
its files are live on `main`. Nothing was blocking it — its red checks belong to
the repo-wide CI defect, not to the PR.

The actual blocker: **every CI job on `main` dies at `Set up job` in ~2–4s**,
before a test runs. Two independent causes:

1. **Six workflow files never registered.** `Auto-Index-Sync.yml` and
   `dependabot-automerge.yml` had an unterminated single-quoted `run:` block that
   swallowed following lines (ScannerError at line 83 / 40). `secret-scan.yml` had
   `workflow_dispatch;` where it needed `workflow_dispatch:`. `test-suite.yml` was
   a prose chat reply wrapped in a code fence. `github-actions-autodebug-autorerun`
   had no `.yml` extension. `release_drafter.yaml` is release-drafter *config*, not
   a workflow.
2. **Fabricated SHAs.** Six refs look pinned but resolve to nothing
   (`actions/checkout@f548e57c…` where v4.4.0 is `11d5960a…`). This is why the
   failures read as mysterious: the refs are well-formed 40-char SHAs, so a shape
   check passes while GitHub rejects them at job setup.

## What was done

Installed `deliverables/ci/workflows-repaired/` (already on `main`) via its own
`install.sh --apply`, into a clean clone of `main`.

**Verified:**

```
python3 deliverables/ci/verify_workflows.py --check-shas
PASS — 11 workflows parse, are shaped correctly, and all 28 action refs are SHA-pinned
```

File-by-file parse: 11/11 clean, versus 4 parse failures on `main`.

## Why it could not be pushed

The Fig GitHub App has no `workflows` scope. Push refused at the transport layer:

```
! [remote rejected] fig/workflow-repair-and-sha-pins ->
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/Auto-Index-Sync.yml` without `workflows` permission)
```

This happens **before a PR can be opened**, so the repair cannot travel as a normal
PR from this App.

**Discriminator (ran this session, conclusive):** a non-workflow push to the *same*
repo in the *same* session **succeeded**. So the block is the App-installation
`workflows` permission — not credentials, not branch rules, not general push failure.

**After the user granted the permission, retried:** push still refused with the
identical error, and an independent workflow-file write through the REST API
returned `403 Resource not accessible by integration`. So the grant has **not yet
taken effect for this installation**. No probe artifact was left on the repo;
`main` is untouched.

## Deliverable

The repair is delivered as **this handoff PR**, which touches only non-workflow
paths so the App can push it:

| Path | Purpose |
|---|---|
| `docs/workflow-repair/workflow-repair-and-sha-pins.patch` | the verified repair diff |
| `scripts/install-workflow-repair.sh` | one command: install → verify → commit → push → PR |
| `docs/workflow-repair/HANDOFF.md` | root cause, evidence, and both landing paths |

A maintainer merges this PR, then runs `bash scripts/install-workflow-repair.sh --apply`
(or grants the App `workflows` write, after which the push can go directly).

## Acceptance criteria

- [x] Root cause identified and reproduced from CI logs
- [x] Repaired set verified with the repo's own gate on a clean tree
- [x] Discriminator run, proving the block is App-level
- [x] Handoff delivered on a branch the App *can* push
- [ ] Repair actually installed on `main` — requires maintainer action or the grant

## Notes

The App-permission ceiling was already recorded in TASK-20260916-002 (PR #311).
This task re-confirmed it and added the API-level 403 probe as a second,
independent proof.
