---
id: TASK-20260910-004
title: Repair the GitHub Actions workflows — YAML errors and unpinned actions
status: new
priority: high
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by: write access to .github/workflows/ (the automation App lacks the workflows permission)
tokens: 0
---

# TASK-20260910-004 — Repair the GitHub Actions workflows

## Goal

Make CI actually run. Today every job fails at the *Set up job* step, so no PR
on this repository can show a green check — even when its own tests pass.

## Scope

- Repair the workflow files that do not parse as YAML.
- Pin every action reference to a full commit SHA, per the org's policy.
- Move non-workflow files out of `.github/workflows/`.

## Out of scope

- Changing what any workflow *does*. Every edit is structural — parse errors and
  reference pinning only.
- Renaming the three mis-named workflow files. Two of them deploy on
  `push: main` / `push: develop`; renaming would start deploys that have never
  run. That is a behaviour change and needs the owner's decision first.

## Steps

- [x] Inspect the repository and measure the real state (do not assume).
- [x] Confirm the failure cause from an actual run log.
- [ ] Move non-workflow files out of `.github/workflows/` into `archive/`.
- [ ] Pin all action refs to full SHAs, resolving each against GitHub.
- [ ] Re-validate every workflow as YAML.
- [ ] Open a PR.

## Acceptance criteria

- [ ] All workflow files parse as YAML (measured: 5 of 12 currently do not).
- [ ] No `uses:` reference uses a mutable tag such as `@v4`.
- [ ] `.github/workflows/` contains only workflow YAML.
- [ ] No workflow's behaviour changes.
- [ ] A PR whose own tests pass shows green checks.

## Dependencies / blockers

**Blocked.** Writing `.github/workflows/` requires the App's `workflows`
permission, which is not granted; pushes are rejected with
`refusing to allow a GitHub App to create or update workflow ... without
workflows permission`. A maintainer must apply this, or the permission must be
raised. Work done earlier in a sandbox was also reclaimed before it could be
committed, so this restarts from current `main`.

## Files changed

| File | Change |
| --- | --- |
| *none yet — blocked before commit* | |

## Validation

| Command | Result |
| --- | --- |
| YAML parse across `.github/workflows/*.y*ml` | **not run yet** — 5 files known broken |
| Count of `uses:` refs still on a tag | **not measured yet** |

## Token usage

Estimated with `len(text) // 4` over the files above: **0**. Not started.

## Notes

Measured on 2026-09-10, `main` still mixes pinned SHAs with mutable tags:
`actions/checkout@v4` (17 refs), `actions/setup-python@v5` (7),
`actions/upload-artifact@v4` (6), `subosito/flutter-action@v2` (5),
`somaz94/compress-decompress@v1` (5), and others.

The five files that do not parse each fail differently: one is wrapped in a
Markdown ```yaml fence, one has a multi-line heredoc inside a `run: |` block,
one has ~87 lines of GitHub documentation appended to the end, one uses a `;`
where a `:` belongs, and one has a flow mapping whose braces nest.

## Completion summary

*Not complete.*
