# CI Workflow SHA-Pin + YAML Repair

The repo's org ruleset requires every GitHub Actions `uses:` reference to be pinned to a
**full 40-character commit SHA**. On `main`, 68 references across 9 workflows were still on
moving tags (`@v4`, `@v5`, `@main`, ...), which fails every job at "Set up job" — and four
workflows did not parse as YAML at all.

The Fig GitHub App lacks the **`workflows`** scope for this repo, so it cannot push changes
under `.github/workflows/` directly. This deliverable carries the verified fix so it can be
applied in one step.

## What was changed

**1. Pinned 68 action references across 9 workflows** to full commit SHAs, resolved from the
upstream tags via the GitHub API and **verified reachable** (23 distinct action@sha pairs,
all HTTP 200 on `github.com/<owner>/<repo>/commit/<sha>`). Each pinned line keeps a trailing
`# vN` comment for readability.

| Workflow | refs pinned |
|---|---|
| build-compress-all-platforms.yml | 29 |
| ci.yml | 13 |
| live-task.yml | 7 |
| static.yml | 4 |
| test-and-coverage.yaml | 4 |
| Auto-Index-Sync.yml | 3 |
| secret-scan.yml | 3 |
| test-suite.yml | 3 |
| dependabot-automerge.yml | 2 |

**2. Repaired 4 workflows whose YAML did not parse on `main`** (pre-existing, not caused by
pinning — confirmed by validating the `HEAD` versions):

- `secret-scan.yml` — `workflow_dispatch;` -> `workflow_dispatch:`
- `dependabot-automerge.yml` — removed 87 lines of appended markdown docs that followed the workflow
- `test-suite.yml` — extracted the YAML body from the markdown code fence it was wrapped in
- `Auto-Index-Sync.yml` — replaced an indentation-breaking single-quoted heredoc with `printf`

No workflow **logic** was changed.

## How to apply

### Option A - apply the patch (recommended)

```bash
git checkout main && git pull
git checkout -b fix/sha-pin-and-yaml-repair
git apply deliverables/ci-workflow-sha-pin/sha-pin-and-yaml-repair.patch
python -c "import yaml,glob;[yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.y*ml')];print('all workflows parse')"
git add .github/workflows && git commit -m "fix(ci): pin all actions to full SHAs and repair broken workflow YAML"
git push -u origin fix/sha-pin-and-yaml-repair
```

### Option B - copy the fixed files

```bash
cp deliverables/ci-workflow-sha-pin/fixed-workflows/*.y*ml .github/workflows/
```

## Verification

Every claim above was checked:

- **YAML**: all 10 root workflows parse with `yaml.safe_load` (0 failures).
- **SHAs**: all 23 distinct `action@sha` pairs return HTTP 200 from their upstream repo — none are
  fabricated, which matters because a prior attempt shipped SHAs that did not exist.
- **Unpinned refs remaining in root workflows**: only `.github/workflows/github-actions-autodebug-autorerun`,
  which has **no `.yml`/`.yaml` extension** so GitHub never runs it, and references
  `ZyntroAI/ai-codefix-action@v1` — **a repository that does not exist**. Left untouched
  deliberately; it is inert.

## Scripts (reproducible)

- `scripts/resolve_shas_api.py` — resolves real SHAs for each tag via the GitHub API
- `scripts/pin_workflows.py` — rewrites `uses:` refs to pinned SHAs (idempotent)
- `scripts/repair_workflows.py` — repairs the four broken YAML files
- `scripts/verify_shas.py` — asserts every pinned SHA exists upstream

## Known limitation

The Fig App cannot push `.github/workflows/` changes for this repo. If applying via a PR,
either use the user's own credentials, or grant the app the `workflows` scope.
