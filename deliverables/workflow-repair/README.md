# Workflow Repair — SHA-pinning + YAML integrity

Repairs every defect that makes this repository's CI fail at the **`Set up job`**
step. Each defect was reproduced against the live default branch, and each fix was
validated by parsing the result.

**Context.** Every PR currently shows red checks that die in 2–3 seconds, before any
checkout or test runs. Neither defect class is caused by the PR that happens to be
open — `main` is red on all five workflows by itself.

## Why this is a patch, not a direct edit

The root `.github/workflows/` path is push-blocked for the Fig App (installation-level
`workflows` permission). This deliverable therefore ships the **fixed files plus a git
patch**, both under this nested path. Apply with:

```bash
git apply deliverables/workflow-repair/workflow-repair.patch
```

Verified: applies cleanly to a fresh clone of `main` (`ff82df5`), and every one of the
11 resulting workflow files is byte-identical to the copies in `.github/workflows/` here.

## Defect class A — four files are not valid YAML at all

GitHub cannot load these at all, so their jobs never run.

| File | What was wrong | Fix |
| --- | --- | --- |
| `secret-scan.yml` | `workflow_dispatch;` — a stray semicolon where a colon belongs. Broke parsing at line 9. | `:` |
| `Auto-Index-Sync.yml` | An embedded Python heredoc inside a `run: \|` block had its continuation lines at column 0, terminating the block scalar. Broke parsing at line 83. | Re-emitted the placeholder as individual `echo`/`printf` appends, correctly indented. |
| `dependabot-automerge.yml` | 87 lines of GitHub documentation appended after the real workflow (`# Navigating code on GitHub` …). | Truncated at line 36. |
| `test-suite.yml` | The whole file was a markdown answer: prose, a ` ```yaml ` fence, the workflow, then more prose. | Extracted the fenced body. |

## Defect class B — one file was never a workflow

| File | What was wrong | Fix |
| --- | --- | --- |
| `github-actions-autodebug-autorerun` | A prose **specification** of a workflow — Thai/English narration, with no `.yml` extension, so GitHub never loaded it. The real YAML starts at the first top-level `name:`. | Extracted 260 lines and wrote them to `auto-debug-rerun.yml` (a rename in the patch). |

Because the old filename had no extension it was inert — which is why it could sit
broken for so long without anyone noticing.

## Defect class C — 70 action refs unpinned or unresolvable

Three sub-cases, all fatal at `Set up job`:

1. **Literal placeholders** — `actions/checkout@<commit-sha>` (3 refs in `test-and-coverage.yaml`).
   Never resolvable; this is the job that fails fastest.
2. **SHA-shaped but non-existent** — `actions/checkout@f548e57c…`, `actions/setup-python@5fda3b9c…`,
   `actions/checkout@11bd7190…`, `codecov/codecov-action@eaaf46c7…`,
   `docker/build-push-action@4a13b6b0…`, `docker/login-action@74a5d146…`,
   `github/codeql-action@977e6ce4…`. All 404 upstream — fabricated, not merely stale.
   GitHub reports these as `Unable to resolve action`.
3. **Floating and invalid tags** — `@v4`, `@v5`, `@v2` …, plus `actions/checkout@v7`,
   which does not exist. The repository's own policy requires full-SHA pins, so even the
   resolvable tags are violations.

**70 refs across 10 files** were rewritten to verified full-length commit SHAs, each with
a trailing `# vN` comment:

```yaml
- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
```

Every SHA was resolved live from its upstream repository and reflects the version the
file already intended — a `@v4` ref resolved to the `v4` tag's commit, never silently
bumped to a newer major.

## Verification

| Check | Result |
| --- | --- |
| All 11 files parse as a single YAML document | **11 / 11 pass** |
| Of those, files that declare `jobs` (i.e. are workflows) | **10 / 11** — `release_drafter.yaml` has none |
| Non-pinned action refs remaining | **0** |
| Patch applies to fresh clone of `main` | clean, no conflicts |
| Fixed tree vs patched clone, byte-for-byte | **11 / 11 identical** |
| Old extensionless file removed by the patch | yes |

Run the repair yourself (dry run by default):

```bash
python3 repair_workflows.py <repo_dir>          # report only
python3 repair_workflows.py <repo_dir> --apply  # write
```

## Files

| File | Purpose |
| --- | --- |
| `workflow-repair.patch` | The complete fix, ready to `git apply` |
| `.github/workflows/` | The 11 fixed files, for review without applying |
| `repair-report.json` | Machine-readable log: every ref edit, every YAML fix |
| `fix_workflow_pins.py` | Pin `uses:` refs to full SHAs |
| `repair_workflows.py` | Repair the three YAML-damage shapes |
| `extract_wrapped_workflows.py` | Recover workflow YAML from markdown-wrapped files |
| `build_repair_set.py` | Orchestrates all of the above and emits the patch |
| `probe_refs.py` | Audit every `uses:` ref against upstream; finds the 404s |

## Flagged, deliberately not changed

- **`release_drafter.yaml` is not a workflow.** Its contents are an `autolabeler:` config
  for release-drafter, which belongs at `.github/release-drafter.yml`. Sitting in
  `.github/workflows/` it has no `on:` or `jobs:`, so GitHub cannot use it as a workflow.
  Moving it is a judgement call about repository layout, so it is reported here rather
  than moved inside a CI-repair patch.
- **`ZyntroAI/ai-codefix-action@v1`** is referenced only inside a prose documentation
  block of the extracted `auto-debug-rerun.yml`, not as a real `uses:` step. Left
  untouched. If that action is meant to be wired up, its repository and tag must exist first.

## One caveat worth stating plainly

Fixing these workflows lets CI *start*. It does not make CI *green*: once the jobs run,
whatever test, lint, and build failures have been masked by the setup failures will
surface. This removes the blocker in front of the signal; it does not guarantee the
signal is clean.
