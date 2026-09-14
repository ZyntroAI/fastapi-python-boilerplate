# Full CI/CD Pipeline — Orchestrated Baseline

Self-contained, SHA-pinned CI/CD pipeline for `ZyntroAI/fastapi-python-boilerplate`.

**Status:** new deliverable (2026-09-14). Does not modify or replace any existing
workflow under `.github/workflows/`. Intended to become the single entry-point
pipeline once reviewed.

---

## Why this exists

The current CI surface is fragmented and partly broken:

| Problem | Evidence (on `main`, 2026-09-14) |
|---|---|
| 5 workflow files fail YAML parsing | `Auto-Index-Sync.yml`, `dependabot-automerge.yml`, `github-actions-autodebug-autorerun`, `secret-scan.yml`, `test-suite.yml` |
| 60 of 73 `uses:` refs are not pinned to a commit SHA | supply-chain risk, non-reproducible runs |
| Overlapping jobs duplicated across files | `ci.yml`, `live-task.yml`, `test-and-coverage.yaml`, `test-suite.yml` all run lint/test |
| No single gate | a PR can merge with some workflows red and others green |

This deliverable collapses the surface into **one orchestrator + two reusable
workflows**, all actions pinned to full commit SHAs.

---

## Layout

```
deliverables/full-cicd-pipeline/
├── .github/workflows/
│   ├── pipeline.yml               # orchestrator — the only entry point
│   ├── reusable-python-ci.yml     # lint · typecheck · test · coverage
│   └── reusable-security-scan.yml # gitleaks · pip-audit · CodeQL
├── validate_pipeline.py           # offline validator (YAML + SHA pinning + job graph)
├── HANDOFF.md                     # how to promote into .github/workflows/
└── README.md                      # this file
```

---

## Pipeline stages

```
            ┌───────────────┐
push/PR ───▶│  orchestrate  │
            └───────┬───────┘
                    │
        ┌───────────┼───────────┬──────────────┐
        ▼           ▼           ▼              ▼
   python-ci   security-scan  docker-build   (gate)
   lint→test→cov   gitleaks      build-only   aggregate
                   pip-audit                   status
                   codeql
```

| Stage | Job | Blocks merge | Trigger |
|---|---|---|---|
| Quality | `python-ci` → lint, typecheck, test, coverage | yes | push `main`/`dev`, all PRs |
| Security | `security-scan` → gitleaks, pip-audit, CodeQL | yes | push, PR, weekly schedule |
| Build | `docker-build` (build-only, no push) | yes on PR | after quality+security |
| Gate | `ci-gate` | yes | always — single required check |

### Design rules

1. **One required check.** Branch protection should require only `ci-gate`.
   Every other job reports into it, so a partially-red matrix can never merge.
2. **Fail-fast.** `python-ci` runs lint before test; a lint failure never spends
   test minutes.
3. **Reusable, not copy-pasted.** Both reusable workflows take typed inputs and
   can be called by future workflows without duplicating steps.
4. **Everything pinned.** Every `uses:` is a 40-char commit SHA with the tag in a
   trailing comment for readability.
5. **Least privilege.** `permissions: contents: read` at the top; elevated scopes
   granted per-job only where required.

---

## Promotion (into the live repo)

`.github/workflows/` at the repo root requires the GitHub App `workflows`
permission, which is **not currently granted**. Two paths:

**A — merge as a deliverable (works today).**
The nested path `deliverables/full-cicd-pipeline/.github/workflows/` is *not*
blocked. Merge this PR, then a human with `workflows` permission copies the three
files up one level. See `HANDOFF.md`.

**B — direct.** Once the `workflows` scope is granted at installation level,
copy the three files into `.github/workflows/` and delete the old ones they
supersede.

---

## Validation

```bash
python validate_pipeline.py
```

Checks: (1) every file parses as YAML, (2) zero unpinned `uses:` refs, (3) every
SHA is 40 hex chars, (4) job graph is acyclic and `needs` targets exist,
(5) `ci-gate` aggregates every real job.
