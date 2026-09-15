# Copilot Free + Actions Hardening Playbook

A working, self-contained playbook for getting near-Pro value out of **GitHub Copilot
Free** and hardening the repo's **GitHub Actions** pipelines — tailored for ZyntroAI's
stack (FastAPI · React · PostgreSQL) and the FIG Framework.

## What's in here

```
copilot-free-actions-playbook/
├── deck/
│   └── index.html          # 14-slide self-contained HTML deck (TH + EN) — open in any browser
├── workflows/
│   ├── deploy-oidc.yml         # Layer 1 — OIDC keyless deploy (no long-lived cloud creds)
│   └── token-health-check.yml  # Layer 3 — probes every token every 6h, alerts Slack
├── scripts/
│   ├── audit_workflows.py      # static audit of .github/workflows for hardening gaps
│   └── test_audit_workflows.py # proves the audit rules fire (and stay quiet on clean input)
└── README.md
```

## The deck

`deck/index.html` is a single self-contained file — no build step, no CDN, no external
assets. Open it directly in a browser, or serve it. Navigate with `←` / `→` / `Space`,
`Home` / `End`, or the on-screen buttons; fullscreen button included.

14 slides in four parts:

1. **Copilot Free (slides 1–7)** — the real Free vs Pro limits, saving completions
   (enable/disable scope + shortcuts), batching chat messages, when chat is worth a
   request vs when it isn't, free alternatives, and usage monitoring.
2. **Token self-healing (8–10)** — OIDC zero-touch, auto-refresh + dual-key rotation,
   and the three self-healing patterns (retry/backoff, auto-refresh on 401, health check).
3. **Actions hardening (11–12)** — SHA pinning, least privilege, injection prevention,
   and the performance/cost levers (caching, concurrency, path filters, retention).
4. **Advanced Copilot skills (13–14)** — 3S+R prompts, custom instructions, slash
   commands, chain prompts, and the phased ZyntroAI rollout order.

Sources are cited on each slide's footer.

## The audit script

A dependency-free static analyser for workflow hardening. Six rules:

| Rule | Level | Catches |
|---|---|---|
| `unpinned-action` | ERROR | `uses:` on a moving tag (`@v4`, `@main`) instead of a full 40-char SHA |
| `broad-permissions` | ERROR | workflow with no top-level `permissions:` block |
| `injection-risk` | ERROR | `${{ github.* }}` used directly inside a `run:` block |
| `no-timeout` | WARN | a job without `timeout-minutes:` |
| `no-concurrency` | WARN | workflow without a `concurrency:` block |
| `long-retention` | WARN | `upload-artifact` without `retention-days:` |

```bash
# scan the current repo's workflows
python3 scripts/audit_workflows.py .github/workflows

# also emit a JSON report
python3 scripts/audit_workflows.py .github/workflows --json audit.json

# prove the rules work
python3 scripts/test_audit_workflows.py
```

Exit code is `1` when any ERROR-level finding is present, so it drops straight into CI
as a gate. It is pure stdlib — no `pip install`, runs anywhere Python 3.9+ does.

### Verified result on this repo

Run against `.github/workflows/` as of this branch:

```
files scanned : 10
findings      : 62 error, 35 warn
clean files   : 0
```

The dominant finding is `unpinned-action`. That matters here because the org ruleset
requires every `uses:` to be a full SHA — which is exactly why `deliverables/ci-workflow-sha-pin/`
exists. Running this script before a workflow PR catches the regression before CI does.

## How to adopt

**Week 1–2 (critical).** Pin actions to SHA; set org default token permissions to
read-only; enable secret scanning + push protection; add `timeout-minutes` to every job;
add `concurrency` to PR-triggered workflows. Run `audit_workflows.py` as the gate.

**Week 3–4 (high).** Replace static cloud credentials with OIDC (`deploy-oidc.yml`);
add environment protection rules; add `CODEOWNERS` for `.github/workflows/*`;
configure Dependabot for `github-actions`; wire `actionlint` into CI.

**Month 2.** Reusable workflows; `paths:` filters for the monorepo; cut artifact
retention to 7 days; set up the usage dashboard.

**Month 3+.** Right-size runners; SLSA provenance; DORA metrics; quarterly audit.

For Copilot itself: keep it enabled only on complex logic, batch chat questions, and
check `github.com/settings/copilot` weekly.

## Notes

- The two workflow templates in `workflows/` are **templates**, not active workflows —
  they live under `deliverables/`, so GitHub will not execute them. Copy one into
  `.github/workflows/` when you're ready to adopt it (that push needs the App's
  `workflows` scope).
- `deploy-oidc.yml` contains a placeholder role ARN and `token-health-check.yml` a
  placeholder API host — replace both before use.
- No secrets are referenced by value anywhere in this deliverable.
