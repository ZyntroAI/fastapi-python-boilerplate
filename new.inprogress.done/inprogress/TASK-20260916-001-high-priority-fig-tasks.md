---
id: TASK-20260916-001
title: High-priority FIG-TASK batch — vite script, ESLint config, .env tracking, workflow repair
status: inprogress
priority: high
created: 2026-09-16
updated: 2026-09-16
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [303]
blocked_by: write access to .github/workflows/ for the workflow half — PROBLEMS.md P-003
tokens: 0
---

# TASK-20260916-001 — High-priority FIG-TASK batch (items 1–4)

## Goal

Work the four 🔴 high-priority items from the FIG-TASK request of 2026-09-16, and
record what was already true so the list can be trusted. Two of the four needed
changing; two did not.

## Scope

- FIG-TASK-001 — `scripts.vite` is a semver range, so `npm run vite` cannot run.
- FIG-TASK-002 — no ESLint config file, so `npm run lint` and `lint-staged` fail.
- FIG-TASK-003 — `.env` tracked in Git despite `.gitignore`.
- FIG-TASK-004 — five files in `.github/workflows/` do not parse.

## Out of scope

- The 🟡 and 🟢 items (FIG-TASK-005 … 011). Not requested in this pass.
- SHA-pinning the remaining refs (FIG-TASK-007). The install kit already carries
  a pinned set; adopting it is FIG-TASK-004, re-pinning is its own task.
- Renaming the mis-named workflow files. Two of them deploy on `push: main`;
  renaming would start deploys that have never run.

## Findings — what was already done, and what was not

Two of the four were already finished before this task started. Verified, not
assumed:

| Item | State found on `main` | Action |
| --- | --- | --- |
| 001 `scripts.vite` | **broken** — `"vite": ">=6.4.3"` | fixed in PR #303 |
| 002 ESLint config | **missing** | fixed in PR #303 |
| 003 `.env` tracked | **already done** — commit `d2d29a4`, and `.gitignore` already covers `.env` and `.env.*` | none needed |
| 004 workflow repair | **already delivered** — the repaired set and install kit are on `main` under `deliverables/ci/` | install is the remaining step |

## Steps

- [x] Inspect the repository and measure the real state (do not assume).
- [x] FIG-TASK-001 — set `scripts.vite` to `"vite"`.
- [x] FIG-TASK-002 — add `eslint.config.mjs`; add `@eslint/js`, `globals`,
      `typescript-eslint` to devDependencies.
- [x] FIG-TASK-003 — confirm already done; no change.
- [x] FIG-TASK-004 — verify the existing repair kit installs and passes.
- [x] Open PR #303 for 001 + 002.
- [ ] Merge PR #303.
- [ ] Apply the workflow repair kit (needs `workflows` permission).

## Acceptance criteria

- [x] `npm run lint` exits 0.
- [x] `npm ci` succeeds on a clean checkout — 693 packages.
- [x] `package.json` diff limited to the `vite` script and the three devDeps.
- [x] The install kit, applied with `--apply`, makes `verify_workflows.py` PASS
      (11 workflows parse, all 28 refs pinned).
- [x] The before-state genuinely fails — `verify_workflows.py` exits 1 on
      unmodified `main`.

## Dependencies / blockers

**Partly blocked.** The workflow half cannot be pushed from here: any push
touching `.github/workflows/` is rejected at the transport layer with
*refusing to allow a GitHub App to create or update workflow … without
`workflows` permission*, before a PR can even be opened. That is **PROBLEMS.md
P-003**. The repaired files already live on `main` under
`deliverables/ci/workflows-repaired/`, so this is an install step, not a
missing deliverable.

**Why `main` is red, confirmed while working this.** The four repaired workflow
files are only half the story. `ci.yml` — the file that runs on every PR — pins
five refs to well-formed 40-hex strings that name **no real commit**:
`actions/checkout@f548e57c…`, `actions/setup-python@5fda3b9c…`, and
`github/codeql-action/{init,autobuild,analyze}@977e6ce…`. Every job listing one
dies in *Set up job* after two seconds. That is why PR #303 is red on `lint`
while `npm run lint` passes locally on the same tree — the failure is before the
checkout, so the job never runs the code at all. Recorded as **P-013**;
`deliverables/ci/workflows-repaired/ci.yml` replaces all five with commits that
resolve.

It is worth keeping separate from P-002 (unpinned tags) because the checks
disagree: a policy check for a 40-hex SHA passes these, while GitHub, which
executes the pin, fails them.

## Files changed

| File | Change |
| --- | --- |
| `package.json` | `scripts.vite` → `"vite"`; three devDeps added |
| `package-lock.json` | regenerated for the new devDeps |
| `eslint.config.mjs` | added — flat config |
| `new.inprogress.done/inprogress/TASK-20260916-001-*.md` | added — this record |
| `CHANGELOG.md` | added entry for the above |
| `.github/workflows/**` | **not changed here** — cannot push; install kit applies from `deliverables/` |

## Validation

| Command | Result |
| --- | --- |
| `npm ci` | exit 0 — 693 packages |
| `npm run lint` | **exit 0**, 0 errors, 1 pre-existing warning |
| `npm run lint` before the fix | failed — *ESLint couldn't find an eslint.config.\* file* |
| `python deliverables/ci/verify_workflows.py` on unmodified `main` | **exit 1** — 5 files unparseable, refs unpinned |
| `install.sh --apply` then `verify_workflows.py` | **PASS** — 11 workflows parse, 28/28 refs pinned |
| `confirm each SHA exists` (`verify_workflows.py --check-shas`) | all 28 real |

## Notes

The ESLint fix is a **flat config**, not the `.eslintrc.cjs` the task list
suggests. The repo pins `eslint ^10.10.0`, which no longer reads `.eslintrc.*`
at all, so the suggested file would have reproduced the same failure. Worth
carrying forward: the task list's proposed fix for 002 would not have worked.

Two files are excluded from linting because they contain pasted chat prose
rather than code — `scripts/pr-manager.js` and `middleware/errorHandler.ts`.
They parse as neither JS nor TS. That is a finding for FIG-TASK-008 (repo-root
cleanup), not something to paper over here.

`.github/workflows/release_drafter.yaml` is a release-drafter *config*, not a
workflow. It parses, so it breaks nothing, but GitHub never runs it. The install
kit moves it to `.github/release-drafter.yml` where release-drafter reads it.

## Completion summary

*Not complete.* PR #303 is open for FIG-TASK-001 and 002. FIG-TASK-003 required
no work. FIG-TASK-004 is a verified install step blocked on `workflows`
permission (P-003).
