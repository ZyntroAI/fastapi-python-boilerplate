---
id: TASK-20260923-002
title: Workflow repair — SHA-pinning + YAML integrity
status: new
priority: high
created: 2026-09-23
updated: 2026-09-23
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by: "root .github/workflows/** is push-blocked for the Fig App (installation-level `workflows` permission)"
tokens: 0
---

# TASK-20260923-002 — Workflow repair

## Goal

Remove the defect that makes every CI run in this repository fail at the
`Set up job` step, before any checkout or test executes, so that CI can
actually run and report on the code.

## Scope

`deliverables/workflow-repair/` — fixed copies of all 11 workflows plus a git
patch that applies them to the repo root, and the scripts that produced them.

## Out of scope

- No application code, tests, or schema changes.
- Not a direct edit of root `.github/workflows/**` — push-blocked for the Fig App.
- Not claiming the tests will pass once CI runs (see caveat in the README).

## Steps

- [x] Reproduce the failure from the live CI logs and identify the failing step.
- [x] Audit every `uses:` ref against upstream (found 70 unpinned / unresolvable).
- [x] Resolve each action tag to a full commit SHA via `git ls-remote`.
- [x] Identify the four files that are not valid YAML and diagnose each.
- [x] Extract the two markdown-wrapped / non-workflow files.
- [x] Build the repair set and validate every file parses.
- [x] Verify the patch applies to a fresh clone and the results are byte-identical.

## Acceptance criteria

- [x] Every workflow parses as a single YAML document with a `jobs` key (11/11).
- [x] Zero non-pinned action refs remain.
- [x] Patch applies cleanly to a fresh clone of `main` (`ff82df5`).
- [x] All 11 resulting files byte-identical to the shipped copies.

## Dependencies / blockers

The repair cannot be applied from this environment: pushes to root
`.github/workflows/**` are refused for the Fig App, which is why this ships as a
patch. Someone with workflow write access must apply it.

## Files changed

| File | Change |
| --- | --- |
| `deliverables/workflow-repair/workflow-repair.patch` | Added |
| `deliverables/workflow-repair/.github/workflows/*` | Added (11 fixed files) |
| `deliverables/workflow-repair/README.md` | Added |
| `deliverables/workflow-repair/*.py` | Added (repair scripts) |
| `deliverables/workflow-repair/repair-report.json` | Added |
| `deliverables/README.md` | Row added, count 31 → 32 |
| `CHANGELOG.md` | Entry under `[2026-09-23]` |

## Validation

| Command | Result |
| --- | --- |
| parse all 11 workflows with PyYAML | 11/11 pass, single document, `jobs` present |
| `grep -rho 'uses: [^ ]*@[^ ]*' \| grep -vE '@[0-9a-f]{40}'` | 0 refs |
| `git apply --check` on fresh clone of `main` | clean |
| sha256 compare fixed tree vs patched clone | 11/11 identical |

## Notes

Three distinct defect classes were found, and each was verified against the live
repo rather than inferred:

1. **YAML damage** in 4 files — the repository had files that GitHub could not load
   at all, which is why no job ever appeared to run for them.
2. **A non-workflow in the workflows directory** — `github-actions-autodebug-autorerun`
   had no `.yml` extension and contained prose, so it was inert. That is why it stayed
   broken unnoticed.
3. **Fabricated SHAs** — several pinned-looking refs (`f548e57c…`, `5fda3b9c…`,
   `11bd7190…`, `977e6ce4…`) return 404 upstream. They were not stale; they never
   existed.

`release_drafter.yaml` is an `autolabeler:` config, not a workflow — flagged in the
README but deliberately left in place, since moving it is a repository-layout
decision rather than a CI repair.

## Completion summary

Fill in when moving to `done/` or `archive/`.
