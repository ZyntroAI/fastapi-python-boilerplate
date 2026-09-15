---
id: TASK-20260915-002
title: Add auto-label skill (conventional-commit type + changed paths)
status: done
priority: normal
created: 2026-09-15
updated: 2026-09-15
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by:
tokens: 0
---

# TASK-20260915-002 — Add auto-label skill

## Goal

A PR that follows the repo's own commit convention should not need a human to
decide which of the 40 labels applies. This routes the mechanical majority
automatically and leaves the rest unlabelled.

## Scope

- `skills/auto-label/SKILL.md` — the contract
- `skills/auto-label/classify.py` — pure `(title, paths) -> set[label]`
- `skills/auto-label/labels.json` — the rule table (data, not code)
- `skills/auto-label/apply.py` — CLI, dry-run by default
- `skills/auto-label/tests/test_classify.py` — runnable, no network
- `deliverables/ci/auto-label.yml` — the workflow, shipped uninstalled
- `deliverables/ci/auto-label.README.md` — install instructions

## Out of scope

- **Installing the workflow.** The GitHub App lacks the `workflows` scope, so
  pushing to `.github/workflows/**` is blocked. The file ships in
  `deliverables/ci/` for manual install, the established pattern.
- **`deliverables/ci/README.md`.** It documents the auto-compress patch. The
  new instructions go in `auto-label.README.md` instead of overwriting it.

## Steps

- [x] Read the repo's real label list and skill layout
- [x] Write the classifier with a data-driven rule table
- [x] Write runnable tests; run them
- [x] Fix a test that expected scope to be a signal (it is not, by design)
- [x] Dry-run against real merged PRs (#292, #293)
- [x] Write the workflow with SHAs resolved from the public API
- [x] Validate the YAML and confirm each SHA exists (HTTP 200)
- [x] Record the entry in CHANGELOG and update the README skill count

## Acceptance criteria

- [x] `python skills/auto-label/tests/test_classify.py` exits 0, all passing.
- [x] `apply.py` is dry-run unless `--apply` is given.
- [x] Applying never removes a label (`addLabels` only).
- [x] A non-matching PR yields an empty set — no default/guess label.
- [x] Every action pin in the workflow resolves to a real commit.
- [x] The workflow file is valid YAML.

## Dependencies / blockers

Workflow installation blocked on the `workflows` scope — delivered as a file,
not a push.

## Note

While verifying the pins this task surfaced a pre-existing defect: `main`'s
`.github/workflows/ci.yml` pins `actions/checkout` to `f548e57c…`, which GitHub
returns HTTP 422 for (no such commit). That is why PRs #293/#294 failed CI at
`Set up job` in 2 seconds. Not fixed here — it needs the `workflows` scope — but
recorded so the next person does not re-diagnose it.
