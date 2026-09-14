# HANDOFF — Promoting the Full CI/CD Pipeline

**Deliverable:** `deliverables/full-cicd-pipeline/`
**Validated:** 2026-09-14 — `python validate_pipeline.py` → `READY` (exit 0)
**Blocker:** GitHub App `fig-ai-agent` lacks the `workflows` installation scope, so
nothing can be written directly to `.github/workflows/` at the repo root.

---

## What you are promoting

Three files, all SHA-pinned, all validated:

```
pipeline.yml                orchestrator — the only entry point
reusable-python-ci.yml      lint · typecheck · test+cov · codecov
reusable-security-scan.yml  gitleaks · pip-audit · CodeQL
```

They land at `.github/workflows/` (repo root). Do not nest them — reusable
workflows are referenced as `./.github/workflows/<name>.yml` and that path is
resolved from the repo root regardless of where the caller lives.

---

## Promote — option A (no `workflows` scope needed)

1. Merge this PR. The files live safely under `deliverables/`.
2. Check out `main` locally and copy the three files up one level:

   ```bash
   git checkout main && git pull
   cp deliverables/full-cicd-pipeline/.github/workflows/*.yml .github/workflows/
   ```

3. Do **not** commit blind — first retire the files this pipeline supersedes.
   The current `main` has 11 files in `.github/workflows/`; reconciliation:

   | Existing file on `main` | Action |
   |---|---|
   | `ci.yml` | delete — superseded by `pipeline.yml` |
   | `test-and-coverage.yaml` | delete — superseded by `reusable-python-ci.yml` (job `test`) |
   | `test-suite.yml` | delete — superseded (and currently YAML-broken) |
   | `live-task.yml` | keep — service-specific, not covered here |
   | `secret-scan.yml` | delete — superseded by `reusable-security-scan.yml` (job `gitleaks`) |
   | `Auto-Index-Sync.yml` | keep — but it is YAML-broken; see the other deliverable |
   | `dependabot-automerge.yml` | keep — but it is YAML-broken; see the other deliverable |
   | `github-actions-autodebug-autorerun` | keep — but it is YAML-broken |
   | `static.yml` | keep — GitHub Pages deploy |
   | `build-compress-all-platforms.yml` | keep — mobile/desktop release builds |
   | `release_drafter.yaml` | keep |

   The SHA-repaired copies of the kept-but-broken files are already prepared in
   `deliverables/ci-workflow-sha-pin/fixed-workflows/`.

4. Validate before pushing:

   ```bash
   python deliverables/full-cicd-pipeline/validate_pipeline.py   # validates the deliverable copy
   python -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*')]; print('all parse')"
   ```

5. Commit and open a PR. Then set branch protection:

   ```
   Settings → Branches → main → Require status checks
   → add exactly one:  CI Gate
   ```

   Only `ci-gate` should be required. It fails if any upstream stage is not
   `success`, so a partially-red matrix can no longer merge.

---

## Promote — option B (once `workflows` scope is granted)

Same steps, but the agent can do them end to end: copy the three files, apply the
reconciliation table, push a branch, open the PR. Ask and it will run.

---

## Verification after promotion

1. Open a scratch PR touching any Python file → confirm `Quality`, `Security`,
   `Build`, and `CI Gate` all appear and the gate goes green.
2. Introduce a deliberate lint error → confirm `Lint` fails, `Test` is skipped
   (fail-fast via `needs: lint`), and `CI Gate` fails.
3. Confirm the weekly `schedule` run appears under Actions at 03:00 UTC Monday.
4. Confirm every `uses:` still shows a 40-char SHA:
   ```bash
   grep -rhoE 'uses: *[^ ]+' .github/workflows/ | grep -vcE '@[0-9a-f]{40}'   # expect 0 for the three new files
   ```

---

## Notes and gotchas

- **`docker/build-push-action` builds but never pushes** on this pipeline. Pushing
  to GHCR needs `packages: write` and a `docker/login-action` step — deliberately
  left out so a fork PR cannot reach the registry. Add it in a separate
  release-tag workflow when you want it.
- **`pip-audit --strict`** fails the build on any advisory. If that is too strict
  for the current dependency set, drop `--strict` or add `--ignore-vuln <ID>` per
  accepted risk — do not silently remove the job.
- **CodeQL needs Advanced setup off.** If code scanning default setup is enabled
  for the repo, the `codeql` job will be a no-op or conflict. Check
  `Settings → Code security` first.
- **`if: always()` on `ci-gate`** is intentional: the gate must run even when an
  upstream job fails, so it can turn red and block the merge. Removing it makes
  a failing pipeline report *skipped*, which GitHub treats as not-required.
