# FastAPI Python Boilerplate — AI-Driven

An opinionated FastAPI monorepo used by ZyntroAI as the starting point for production
AI services, agent tooling, and reference documentation. It ships an OAuth2 PKCE API
core, a GraphQL layer, a React frontend, a library of reusable AI-agent skills,
self-contained deliverable suites, and a reference docs library.

> This README reflects the repository as it actually stands on `main`. Sections marked
> **Known state** record things that are incomplete or broken rather than describing
> intent; sections marked **Target state** record policy we intend to reach but have not
> implemented yet. Individual suites under `deliverables/` carry their own READMEs with
> more detail.

---

## What's inside

| Path | Purpose |
| ---- | ------- |
| `main.py` | OAuth2 PKCE API entrypoint — `uvicorn main:app` (`/auth`, `/auth/callback`, `/health`) |
| `app/` | Application package (75 files): `api/`, `core/`, `services/`, `db/`, `routes/`, `integrations/` |
| `app/core/main.py` | A second, fuller FastAPI app (items/users routers, DB session, origin middleware) |
| `graphql_api/` | Standalone GraphQL service — Strawberry + async SQLAlchemy + JWT + Alembic, own `requirements.txt`, `docker-compose.yml`, tests |
| `frontend/` | React 18 + Vite + TypeScript frontend (own `package.json`, `Dockerfile`, `tsconfig.json`) |
| `skills/` | 12 reusable AI-agent skill definitions — `fetching`, `research`, `patch`, `credential-management`, `changelog-auto-update`, `pr-triage-automove`, `ci-workflow-authoring`, … |
| `deliverables/` | 27 self-contained feature suites, each with its own README and tests — see [`deliverables/README.md`](./deliverables/README.md) |
| `docs/` | Reference library (54 files): GraphQL, FireCrawl, Google Chat, GitHub Actions, MCP, environment configuration, incident drills, release notes, FIG architecture |
| `tests/` | Test suite — `unit/`, `e2e/`, plus repo-level tests (`tests/conftest.py`, `pytest.ini` at root) |
| `helm/`, `k8s/` | Deployment — Helm chart (`oauth-app`) and Kubernetes manifests (deployment, HPA, ingress, monitoring) |
| `.github/workflows/` | 11 workflow files — only 6 of which parse, so the rest never run; see [CI/CD](#cicd--supply-chain-integrity) |
| `docker-compose.yml` | Local platform stack: Postgres 16, Redis 7, MinIO, Gitea, Prometheus, Grafana, Traefik, stripe-mock |

---

## Quick start

### 1. The OAuth2 API

```bash
cp .env.example .env        # then fill in the values (see Configuration)
pip install -r requirements.txt
uvicorn main:app --reload
```

- Swagger UI — `http://localhost:8000/docs`
- Health — `http://localhost:8000/health`
- Root — `http://localhost:8000/`

### 2. The local platform stack

```bash
docker compose up -d
```

Brings up Postgres, Redis, MinIO, Gitea, Prometheus, Grafana, Traefik and a Stripe
mock — the backing services the suites and integration examples expect.

### 3. The React frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. A deliverable suite

Every suite under `deliverables/` is self-contained. Several ship their own
`docker-compose.yml` plus a seed script, so a fresh clone is one command from a
running stack — for example `deliverables/product-crud/`.

---

## Entrypoints — there are three

The repository contains three separate `app = FastAPI(...)` definitions. Which one
you run depends on what you want:

| Module | Run with | What it is |
| ------ | -------- | ---------- |
| `main.py` | `uvicorn main:app` | The documented OAuth2 PKCE API. Routers: `/auth`, `/auth/callback`, `/health`. |
| `app/main.py` | `uvicorn app.main:app` | Identical to `main.py` (same content, different import path). |
| `app/core/main.py` | `uvicorn app.core.main:app` | The fuller application: items/users routers, DB init/close lifespan, origin validation, gzip, OpenAPI customisation. |

`main.py` and `app/main.py` are duplicates of each other — pick one. `app/core/main.py`
is a different, more complete application and is the more likely base for real work.
This duplication is a known cleanup item, not an intentional layering.

---

## Configuration

`.env.example` is the template. The settings class is `app/core/config.py` (Pydantic
Settings), and it reads the same `.env`.

**Required:**

| Variable | Notes |
| -------- | ----- |
| `OAUTH_CLIENT_ID` | No default — the app will not start without it |
| `OAUTH_CLIENT_SECRET` | Optional; PKCE does not need a client secret |

**Common:**

| Variable | Default | Notes |
| -------- | ------- | ----- |
| `ENV` | `local` | `local` \| `vercel` \| `production` — selects callback URL, frontend URL, and whether `/docs` is exposed |
| `JWT_SECRET` | placeholder | **Change in production** |
| `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES` | `HS256` / `60` | |
| `REDIS_URL` | unset | Optional — token storage |
| `CREDENTIAL_BROKER_URL` / `BROKER_TOKEN` | unset | Central credential broker (metadata only; no raw secrets) |

Callback and frontend URLs are derived from `ENV` — see `OAUTH_CALLBACK_URL` and
`FRONTEND_URL` in `app/core/config.py`.

> **Known state — `.env` is tracked in git.** Despite `.gitignore` listing `.env`, the
> file is committed and carries live third-party keys. Treat it as compromised: move
> those values into CI secrets, rotate them, and `git rm --cached .env`. The tracked
> file is also incomplete relative to the settings class — it has no `OAUTH_CLIENT_ID`,
> so a fresh clone cannot start the API as-is.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

`pytest.ini` sets `asyncio_mode = auto`. `requirements-dev.txt` layers pytest,
pytest-asyncio, pytest-cov and httpx on top of the runtime requirements, plus the
repo's lint toolchain (ruff, black, isort, mypy).

Tests live in `tests/` (`unit/`, `e2e/`, and repo-level files) and inside individual
deliverable suites. Run a suite's own tests from its directory.

> **Known state — the root suite does not collect.** `app/core/config.py` declares
> `OAUTH_CLIENT_ID: str` as a required field, and no environment block supplies it, so
> collection fails before any test runs. Set `OAUTH_CLIENT_ID` (any non-empty value) in
> the environment to collect. Some root test files also use hyphenated names
> (`test-escalation.py`), which pytest cannot import as modules; those were written as
> runnable scripts.

---

## Deliverables

`deliverables/` holds 27 self-contained suites. Each is a complete piece of work —
code, tests, and its own README — rather than a fragment of the main app:

`agent-core` · `agent-security-suite` · `agent-skill-template` · `ai-agent-skills` ·
`ai-agents-decision-pack` · `ai-gateway-architecture-review` · `azure-cli-2026` · `ci` ·
`copilot-free-actions-playbook` ·
`ci-workflow-sha-pin` · `cwe1321-protection-suite` · `docs-verify` · `fastapi-obsidian-backend` ·
`fig-best-practices` · `firecrawl-fastapi` · `full-cicd-pipeline` · `gemini-cli-skills` ·
`gh-devops-toolkit` · `manus-client` · `notebooklm-access-suite` · `notebooklm-link-share` ·
`official-docs` · `onspace-ai` · `onspace-platform-integration` · `pm-backend` ·
`product-crud` · `pure-agent-dev`

See [`deliverables/README.md`](./deliverables/README.md) for one-line descriptions and
links into each suite.

---

## Documentation

[`docs/README.md`](./docs/README.md) is the index. Highlights:

- **MCP** — [`docs/MCP-Guide-Complete.md`](./docs/MCP-Guide-Complete.md), a troubleshooting guide, plus `scripts/check-mcp-environment.sh` (checks Google Cloud ADC, runtimes, and API keys; never prints secret values)
- **Security** — [`docs/knowledge-ai-agent-security-devsecops-2026.md`](./docs/knowledge-ai-agent-security-devsecops-2026.md): sandbox design, trust tiers, state isolation
- **GitHub / DevOps** — [`docs/github-cli-gh-reference.md`](./docs/github-cli-gh-reference.md), [`docs/research-tools-free-guide.md`](./docs/research-tools-free-guide.md), `docs/github-actions/`
- **Integrations** — `docs/GraphQL/`, `docs/FireCrawl_REST_API/`, `docs/GoogleChat_REST_API/`, `docs/supabase.md`
- **FIG** — `docs/fig/`: FIG v4.1 Organization Edition — architecture, governance, MasterFiles policy and security layer, with the spec as machine-readable JSON config under `docs/fig/config/` and a validator (`docs/fig/validate_config.py`)

Also at the root: [`ROADMAP.md`](./ROADMAP.md) (8-phase plan and milestone M4),
[`TASKS.md`](./TASKS.md), [`CHANGELOG.md`](./CHANGELOG.md),
[`PROBLEMS.md`](./PROBLEMS.md) for open blockers,
[`SECURITY.md`](./SECURITY.md), [`CONTRIBUTING.md`](./CONTRIBUTING.md),
[`RELEASE.md`](./RELEASE.md).

---

## Branch model

`main` is the **default and protected integration branch**. Pull requests target it.

`Origin` also exists in this repository. It is **not** the default branch, it is not
currently kept in sync with `main` (the two point at different commits), and no
workflow triggers on it. Treat it as a legacy/parallel branch rather than the
integration point for new work — if we decide to adopt it as the primary branch, that
is a migration to perform deliberately, not a description of today.

```text
main  (default, protected — PRs land here)
 │
 ├── fig/*             automation branches (use this prefix — see below)
 ├── chore/*
 ├── ci/*
 └── <your-branch>
```

> **Known state — branch naming.** Git rejects a push of `X/…` when a ref named exactly
> `X` already exists (*“directory file conflict”*). This remote carries single-segment
> refs `Origin`, `M`, `github`, `main` and `main-1`, so avoid branches named
> `github/…`, `main/…`, `origin/…` or `m/…`. `fig/` is what the automation uses and is
> known to work. The remote also carries ~30 stale `zyntromedia-patch-*` and
> `zyntromedia-*` branches that could be pruned.

### Branch protection

Settings → Branches protection on `main` is **not readable by the automation App**
(the permissions API returns 403), so this README cannot state what rules are actually
enforced. `.github/CODEOWNERS` exists and `.github/dependabot.yml` exists. Confirm the
live rules from the repository settings page before relying on any specific gate.

---

## CI/CD & supply-chain integrity

The repository's policy is **full-SHA pinning**: every `uses:` reference should point at
a 40-character commit SHA, never a mutable tag such as `@v4`.

**Known state (verified 2026-09-14 against `main`):**

- Of the `uses:` references in `.github/workflows/`, **13 are SHA-pinned and 60 still
  use tags** (73 references in all) (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
  `github/codeql-action/*@v3`, and others). `ci.yml` itself is correctly pinned.
- **Five of the eleven files under `.github/workflows/` are not valid YAML, so GitHub
  never runs them.** A predecessor table in `PROBLEMS.md` listed `ci.yml` among them;
  that was wrong — `ci.yml` was repaired by PR #230 and parses at every commit since.
  The five that are actually broken:

  | File | Defect |
  | ---- | ------ |
  | `.github/workflows/secret-scan.yml` | `workflow_dispatch;` — a `;` where a `:` belongs |
  | `.github/workflows/dependabot-automerge.yml` | 87 lines of pasted GitHub docs appended after valid YAML |
  | `.github/workflows/Auto-Index-Sync.yml` | 4 lines escaped the `run: \|` block indentation |
  | `.github/workflows/test-suite.yml` | the workflow is wrapped in prose and a ` ```yaml ` fence |
  | `github-actions-autodebug-autorerun` | a 417-line specification with no extension — never a workflow |

  All five are one defect: assistant output pasted into a file under `workflows/` and
  never validated. `release_drafter.yaml` parses but declares no job — it is a
  release-drafter configuration in the wrong directory (`PROBLEMS.md` P-011).
- **A verified repair exists but is not yet on `main`.** `ci.yml` aside, the fix for all
  five is in [`patches/pr-repair-workflows.patch`](./patches/pr-repair-workflows.patch);
  `git apply --check` confirms it applies clean to `main`, and after applying,
  `yaml.safe_load` parses 10/10 files each with a real `jobs:` key.
- Because those jobs could not start, a feature PR shows red checks even when its own
  tests pass. **Verify a PR in a clean venv rather than trusting the roll-up.** Background
  in [`CHANGELOG.md`](./CHANGELOG.md) and [`PROBLEMS.md`](./PROBLEMS.md).

Fixing workflows needs write access to `.github/workflows/`, which the automation App
does not hold — it must be applied by a maintainer. See [`SECURITY.md`](./SECURITY.md)
for the policy.

### Deployment environments

Seven environments exist (Settings → Environments). The ones that carry rules today:

| Environment | Protection |
| ----------- | ---------- |
| `main` | 15-minute wait timer before deploy |
| `github-pages` | Restricted to custom branch policies |
| `Production`, `Preview`, `copilot` | No protection rules configured |

`Production – fastapi-python-boilerplate-77y5` and
`Production – fastapi-python-boilerplate-y2me` are Vercel-created per-deployment
environments, not durable stages.

---

## Repository hygiene — known state

- **The root carries 227 entries.** Loose scripts, dashboard exports, notebook HTML,
  archives, and chat exports sit alongside the real tree. It has not been pruned or
  classified. Expect to have to look around.
- **The root Node tooling is declared but not wired up.** `package.json` lists `vercel`,
  `eslint`, `prettier`, `vitest` and `semantic-release`, but there is **no ESLint config**
  at the root (so `npm run lint` fails), **no `.releaserc`** for semantic-release, and
  **`scripts.vite` holds a version range (`">=6.4.3"`) where a command belongs.**
  `package-lock.json` exists but should be regenerated before trusting it. Treat the root
  Node path as present but unverified.
- **The root `Dockerfile` does not build the Python API.** It is a Node multi-stage build
  (`node:26-alpine`, `EXPOSE 4000`, `CMD ["node", "dist/index.js"]`). The Python app has
  its own `app/Dockerfile`, and `Dockerfile.txt` is a quoted Dockerfile stored as text
  (with an Alpine/pgloader importer stage and a uv-based Python agent stage) rather than
  a usable file.
- **`uvicorn main:app --reload` starts the OAuth API, not the main application.**
  See [Entrypoints](#entrypoints--there-are-three).

---

## Target state — governance (not implemented)

The items below come from the org governance model. **None of them exist in this
repository today** — they are listed so the gap is explicit, and so nobody mistakes a
document for a control.

| Intended control | Present? | Reality today |
| ---------------- | -------- | ------------- |
| `masterfiles/`, `config/`, `system/`, `settings/` protected paths | **No** | None of these paths exist; no guard workflow exists |
| `masterfiles-guard.yml` (READ/WRITE/UPDATE/DELETE validation) | **No** | No such workflow |
| CodeQL / container scan (Trivy, Grype, Docker Scout) workflows | **No** | `secret-scan.yml` exists but does not parse |
| Signed commits, 2-approval gate, code-owner review | **Unknown** | Not readable via the App; confirm in repo settings |
| SBOM generation, SLSA provenance, artifact signing, OIDC cloud auth | **No** | Not configured |
| FIG v4 RBAC / audit-logging integration | **No** | Not wired to this repository |

Until these exist, treat the corresponding policy as **aspirational**. A `SKILL.md` or
README cannot enforce anything — only a workflow with permissions can.

Recommended order of attack, highest value first:

1. Repair the five unparseable workflows so CI can be trusted at all.
2. Convert the remaining 60 tag-pinned `uses:` references to full SHAs.
3. Get `.env` out of git and rotate the keys it exposed.
4. Prune the stale `zyntromedia-*` branches and classify the root.

# GitHub Community Discussions

In this repository, you will find categories for various product areas. Feel free to share feedback, discuss topics with other community members, or ask questions.

## Product Feedback

| **Feedback Category** | **About the Product** 	|
|---	|---	|
| 👍 [Accessibility](https://github.com/orgs/community/discussions/categories/accessibility) | [About Accessibility](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/managing-accessibility-settings#about-accessibility-settings) |
| 🚢 [Actions](https://github.com/orgs/community/discussions/categories/actions) | [GitHub Actions](https://github.com/features/actions) |
| 🔗 [Apps, API and Webhooks](https://github.com/orgs/community/discussions/categories/apps-api-and-webhooks) | [GitHub Apps](https://docs.github.com/en/apps), [GitHub REST API](https://docs.github.com/en/rest), [GitHub GraphQL API](https://docs.github.com/en/graphql), and [GitHub Webhooks](https://docs.github.com/en/webhooks) |
| 🤖 [Code Security](https://github.com/orgs/community/discussions/categories/code-security) | [GitHub Code Security](https://github.com/features/security) |
| 💻 [Codespaces](https://github.com/orgs/community/discussions/categories/codespaces) | [GitHub Codespaces](https://github.com/features/codespaces) |
| :copilot: [Copilot Conversations](https://github.com/orgs/community/discussions/categories/copilot-conversations) | [GitHub Copilot](https://copilot.github.com/) |
| 🗣️ [Discussions](https://github.com/orgs/community/discussions/categories/discussions) | [GitHub Discussions](https://docs.github.com/en/discussions) |
| 🏢 [Enterprise](https://github.com/orgs/community/discussions/categories/enterprise) | [GitHub Enterprise](https://docs.github.com/en/enterprise-cloud@latest) |
| 🎒 [GitHub Education](https://github.com/orgs/community/discussions/categories/github-education) | [GitHub Education](https://education.github.com/) |
| 🏆 [GitHub Learn](https://github.com/orgs/community/discussions/categories/github-learn) | [GitHub Certifications](https://resources.github.com/learn/certifications/), [Learning Pathways](https://resources.github.com/learn/pathways/), and [GitHub Skills](https://skills.github.com/) |
| 📱 [Mobile](https://github.com/orgs/community/discussions/categories/mobile) | [GitHub Mobile](https://github.com/mobile) |
| 🟥 [npm](https://github.com/orgs/community/discussions/categories/npm) | [npm](https://docs.npmjs.com/) |
| 📦 [Packages](https://github.com/orgs/community/discussions/categories/packages) | [GitHub Packages](https://github.com/features/packages) |
| 💡 [Programming Help](https://github.com/orgs/community/discussions/categories/programming-help) | General programming questions and help |
| 🐙 [Projects and Issues](https://github.com/orgs/community/discussions/categories/projects-and-issues) | [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects) / [GitHub Issues](https://github.com/features/issues) |
| ✔️ [Pull Requests](https://github.com/orgs/community/discussions/categories/pull-requests) | [GitHub Pull Requests](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) |
| 🗳️ [Repositories](https://github.com/orgs/community/discussions/categories/repositories) | [GitHub Repositories](https://docs.github.com/en/repositories) |
| 👋 [Welcome to GitHub](https://github.com/orgs/community/discussions/categories/a-welcome-to-github) | Community introductions — say hi and share what you're working on |
| 🧩 [Other Features and Feedback](https://github.com/orgs/community/discussions/categories/other-feature-feedback-questions-ideas) | [Code Search & Navigation](https://cs.github.com/about), [Feed](https://github.blog/2022-03-22-improving-your-github-feed/), [Lists](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars#organizing-starred-repositories-with-lists), [Models](https://github.com/features/preview/copilot-models), [Pages](https://docs.github.com/en/pages), [Profile](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/about-your-profile), and [Sponsors](https://github.com/sponsors) |

These discussions are where you can share suggestions for how the products should be improved and discuss those improvements with the community, including members of the GitHub product team. Check out [Making suggestions](#making-suggestions) to learn how to provide feedback.

## Discussions Categories

When creating a new post, make sure to choose the predetermined category that best fits your topic. This will ensure that conversations are indexed by their corresponding product or feature, to help community members quickly find answers to their questions.

This repository works in conjunction with the [GitHub public product roadmap](https://github.com/github/roadmap), which is where you can learn about what features we're working on, and when they'll be available. Accordingly, the Issues feature of this repository has been disabled. Discussion categories have been established for specific features listed above, as well as a general category for other topics. Additional categories may be added in the future. In the meantime, topics outside of the listed categories above, will be transferred into the General category. Please review the [CODE OF CONDUCT](https://docs.github.com/en/site-policy/github-terms/github-community-forum-code-of-conduct) before participating in discussions.

## Making suggestions

We encourage you to [open a discussion](https://github.com/orgs/community/discussions) if you have suggestions for how we can improve our products. You don't need to have a solution to the problem you are facing to kick off a discussion. 

Prior to creating a new discussion, please take a look at previous discussions to see if someone else has already shared your suggestion(s). If you find a similar discussion, reply with additional details or upvote the discussion to signal your support rather than creating a new one.

### From a suggestion to a shipped feature

Once you kick off a discussion, the GitHub product team will evaluate the feedback but will not be able to respond to every submission. From there, we will work with you, and the entire community, to ensure we understand the current capabilities GitHub doesn’t have and explore the space for potential solutions to your problem statement:

- If the product team determines that we are going to prioritize a feature to solve the problem you've identified, we may open an issue and track its development in the [public roadmap](https://github.com/github/roadmap).
- If the product team determines that we will not be working to solve the problem you have identified, we may comment on the discussion describing our reasoning so our decisions can remain transparent.

## Disclaimer

Any statement in this repository that is not purely historical is considered a forward-looking statement. Forward-looking statements included in this repository are based on information available to GitHub as of the date they are made, and GitHub assumes no obligation to update any forward-looking statements. The forward-looking comments in the public feedback discussions do not represent a commitment, guarantee, obligation or promise to deliver any product or feature, or to deliver any product and feature by any particular date, and are intended to outline the general development plans. Customers should not rely on these public feedback discussions to make any purchasing decision.
---

## License

MIT — see [LICENSE](./LICENSE).
