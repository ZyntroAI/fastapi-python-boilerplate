---
id: TASK-20260915-003
title: Repair the 6 broken workflows in ZyntroAI/fastapi-python-boilerplate
status: done
priority: high
created: 2026-09-15
updated: 2026-09-26
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [332]
blocked_by:
tokens: 0
---

# TASK-20260915-003 — Repair the broken workflows

## Goal

Every CI run on `main` was red. The cause was not the code: six of eleven
workflow files could not be parsed or registered by GitHub at all, and the one
that could pinned actions to commits that do not exist.

## What was actually wrong

| File | Root cause |
| --- | --- |
| `secret-scan.yml` | `workflow_dispatch;` — a stray semicolon. YAML read the rest of the line as another mapping key. |
| `Auto-Index-Sync.yml` | A single-quoted shell string spanning multiple lines. YAML cannot scan a multi-line quoted scalar; the inner quote had to be closed. |
| `dependabot-automerge.yml` | 6,190 characters of GitHub UI documentation ("Navigating code on GitHub") pasted onto the end of the file. |
| `test-suite.yml` | The file was a chat reply: prose intro, horizontal rule, and the workflow wrapped in a ```` ```yaml ```` fence — plus 42 lines of trailing prose. |
| `github-actions-autodebug-autorerun` | A spec document saved without an extension. Real YAML began at line 29; a second prose block started at line 305. |
| `release_drafter.yaml` | Not a workflow at all — a 16-line release-drafter *config*, filed in the workflows directory, so GitHub registered it as an always-failing workflow. |

Plus: **73 action refs, 60 of them unpinned**, including three fabricated SHAs
and five literal placeholders (`@<commit-sha>`, `@<pin-latest-sha>`).

## Steps

- [x] Audit all 11 files (parse / shape / pin format)
- [x] Verify each pin against the API — found 3 fabricated SHAs (HTTP 422/404)
- [x] Resolve 26 action tags to real commit SHAs
- [x] Repair the 6 broken files
- [x] Move the release-drafter config and give it the workflow it was missing
- [x] Pin all 73 refs
- [x] Verify: parse, shape, shell syntax, SHA existence

## Acceptance criteria

- [x] All 11 files parse as YAML and expose `jobs:`
- [x] All 59 `run:` blocks are valid bash
- [x] All 28 unique action refs are 40-hex SHAs that exist
- [x] `deliverables/ci/verify_workflows.py` exits 0

## Note

The repo's own linter (`lint.py`) checks only that a pin *looks* like a SHA —
40 hex characters. A fabricated SHA passes that check and then fails every job
at `Set up job`, which is how this went unnoticed. `verify_workflows.py`
resolves each SHA against the real repository, so it catches the class of
defect that shape-checking cannot.
