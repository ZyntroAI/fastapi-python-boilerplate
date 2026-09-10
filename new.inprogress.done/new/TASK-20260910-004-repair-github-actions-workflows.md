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
prs: [168]
blocked_by: write access to .github/workflows/ (the automation App lacks the workflows permission) — PROBLEMS.md P-003
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
- [x] Move non-workflow files out of `.github/workflows/` — shipped in
      **PR #168** (7 files moved to `archive/workflows-junk/`).
- [x] Pin all action refs to full SHAs, resolving each against GitHub —
      prepared and verified; **cannot push** (see Blockers).
- [x] Re-validate every workflow as YAML — prepared and verified; cannot push.
- [ ] Open a PR — **blocked**.

## Acceptance criteria

- [ ] All workflow files parse as YAML (measured: 5 of 12 currently do not).
- [ ] No `uses:` reference uses a mutable tag such as `@v4`.
- [x] `.github/workflows/` contains only workflow YAML — done in PR #168.
- [ ] No workflow's behaviour changes.
- [ ] A PR whose own tests pass shows green checks.

## Dependencies / blockers

**Blocked.** Writing `.github/workflows/` requires the App's `workflows`
permission, which is not granted; pushes are rejected with
`refusing to allow a GitHub App to create or update workflow ... without
workflows permission`. Isolated by a control push: a branch touching no
workflow file pushes fine in the same session.

Recorded as **PROBLEMS.md P-003** (the permission block), **P-001** (the five
files that do not parse) and **P-002** (the unpinned refs).

## Files changed

| File | Change |
| --- | --- |
| `archive/workflows-junk/` (7 files) | moved out of `.github/workflows/` — **PR #168, merged** |
| `.github/workflows/` (11 files) | prepared: 5 YAML repairs + 76 refs pinned to full SHAs — **not yet pushed** |

## Validation

| Command | Result |
| --- | --- |
| `yaml.safe_load` across every workflow-shaped file | **5 of 12 FAIL** (names + parser error in P-001) |
| count of `uses:` refs still on a tag | **66** on current `main` |
| prepared fix — re-validate YAML | 11/11 parse |
| prepared fix — pinned refs | 76 total, **0 unpinned** |
| prepared fix — `ci.yml` line endings | 106 CRLF preserved |
| prepared fix — `git apply --check` on current `main` | applies cleanly |

## Notes

The five files that do not parse each fail differently: one is wrapped in a
Markdown ```yaml fence, one has a multi-line heredoc inside a `run: |` block,
one has ~86 lines of GitHub documentation appended, one uses a `;` where a `:`
belongs, and one has a flow mapping whose braces nest.

Do not confuse this task with the CI being *fixed*. Measured on 2026-09-10,
`main` is still red; the repairs exist as a verified patch but are not on the
remote.

## Completion summary

*Not complete.* One step shipped (PR #168). The rest is blocked and is now
owned by `PROBLEMS.md` **P-001**, **P-002** and **P-003**.
