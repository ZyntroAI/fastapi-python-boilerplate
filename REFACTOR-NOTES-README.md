# FastAPI Python Boilerplate — AI-Driven

An opinionated FastAPI monorepo used by ZyntroAI as the starting point for production
AI services, agent tooling, and reference documentation. It ships an OAuth2 PKCE API
core, a GraphQL layer, a React frontend, a library of reusable AI-agent skills,
self-contained deliverable suites, and a reference docs library.

> This README reflects the repository as it actually stands on `main`. Sections marked
> **Known state** record things that are incomplete or broken rather than describing
> intent. Individual suites under `deliverables/` carry their own READMEs with more detail.

---

## What's inside

| Path | Purpose |
| ---- | ------- |
| `main.py` | OAuth2 PKCE API entrypoint — `uvicorn main:app` (`/auth`, `/auth/callback`, `/health`) |
| `app/` | Application package (75 files): `api/`, `core/`, `services/`, `db/`, `routes/`, `integrations/` |
| `app/core/main.py` | A second, fuller FastAPI app (items/users routers, DB session, origin middleware) |
| `graphql_api/` | Standalone GraphQL service — Strawberry + async SQLAlchemy + JWT + Alembic, own `requirements.txt`, `docker-compose.yml`, tests |
| `frontend/` | React 18 + Vite 8 + TypeScript frontend (own `package.json`, `Dockerfile`, `tsconfig.json`) |
| `skills/` | Reusable AI-agent skill definitions (`fetching`, `changelog-auto-update`, `credential-management`, `patch`, `research`, …) |
| `deliverables/` | 21 self-contained feature suites, each with its own README and tests — see [`deliverables/README.md`](./deliverables/README.md) |
| `docs/` | Reference library (30 files): GraphQL, FireCrawl, Google Chat, GitHub Actions, MCP, incident drills |
| `tests/` | Test suite — `unit/`, `e2e/`, plus repo-level tests (`tests/conftest.py`, `pytest.ini` at root) |
| `helm/`, `k8s/` | Deployment — Helm chart (`oauth-app`) and Kubernetes manifests (deployment, HPA, ingress, monitoring) |
| `.github/workflows/` | 13 workflow files — CI/CD, release drafter, secret scan, coverage, auto-index |
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
> file is committed and carries real keys (BytePlus credentials and WhatsApp Cloud API
> tokens). Treat it as compromised: move those values into CI secrets, rotate them, and
> `git rm --cached .env`. The tracked file is also incomplete relative to the settings
> class — it has no `OAUTH_CLIENT_ID`, so a fresh clone cannot start the API as-is.

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

`deliverables/` holds 21 self-contained suites. Each is a complete piece of work —
code, tests, and its own README — rather than a fragment of the main app:

`agent-core` · `agent-security-suite` · `agent-skill-template` · `ai-agent-skills` ·
`ai-agents-decision-pack` · `ai-gateway-architecture-review` · `azure-cli-2026` ·
`cwe1321-protection-suite` · `fastapi-obsidian-backend` · `firecrawl-fastapi` ·
`gemini-cli-skills` · `gh-devops-toolkit` · `manus-client` · `notebooklm-access-suite` ·
`notebooklm-link-share` · `onspace-ai` · `onspace-platform-integration` · `pm-backend` ·
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

Also at the root: [`ROADMAP.md`](./ROADMAP.md) (8-phase plan and milestone M4),
[`TASKS.md`](./TASKS.md), [`CHANGELOG.md`](./CHANGELOG.md),
[`PROBLEMS.md`](./PROBLEMS.md) for open blockers,
[`SECURITY.md`](./SECURITY.md), [`CONTRIBUTING.md`](./CONTRIBUTING.md),
[`RELEASE.md`](./RELEASE.md).

---

## CI/CD & supply-chain integrity

The repository's policy is **full-SHA pinning**: every `uses:` reference should point at
a 40-character commit SHA, never a mutable tag such as `@v4`.

**Known state (verified 2026-09-13 against `main`):**

- Of the `uses:` references in `.github/workflows/`, **20 are SHA-pinned and 61 still
  use tags** (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
  `github/codeql-action/*@v3`, and others). `ci.yml` itself is correctly pinned.
- **Five workflow files are not valid YAML as committed, so they never run:**

  | File | Parse error |
  | ---- | ----------- |
  | `.github/workflows/Auto-Index-Sync.yml` | invalid simple key |
  | `.github/workflows/dependabot-automerge.yml` | invalid simple key |
  | `.github/workflows/secret-scan.yml` | invalid simple key |
  | `.github/workflows/test-suite.yml` | more than one document in the stream |
  | `.github/workflows/github-actions-autodebug-autorerun` | mapping values not allowed (and it has no `.yml`/`.yaml` extension, so Actions ignores it regardless) |

- Because several jobs cannot start, a feature PR can show red checks even when its own
  tests pass locally. Background and the repair history are in
  [`CHANGELOG.md`](./CHANGELOG.md) and [`PROBLEMS.md`](./PROBLEMS.md).

Fixing workflows needs write access to `.github/workflows/`, which the automation App
does not hold by default — it must be applied by a maintainer or with elevated App
permissions. See [`SECURITY.md`](./SECURITY.md) for the policy.

---

## Repository hygiene — known state

- **The root carries 212 entries.** Loose scripts, dashboard exports, notebook HTML,
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
- **`app/services/__init__.py` used to break every service import.** It did
  `from .users import UserService`, a class that has never existed in this package
  (`users.py` defines `UserRepo`, `get_repo`, `fanout_profile`). Because a package
  `__init__` runs first, that one wrong name stopped `app.main` — the entrypoint in
  `app/Dockerfile` — from importing at all. It now carries no package-level imports,
  matching `app/__init__.py`.
- **`settings` has two sources.** `app/core/config.py` (the fuller one, requires
  `OAUTH_CLIENT_ID`) and `app/config.py` (a thin one that defaults `ENV` to
  `production`). `app/core/security.py` and `token_service.py` read `JWT_SECRET_KEY`
  from the first and `JWT_SECRET` from the second — two different keys. Worth unifying.
- **The root suite does not collect.** Covered under [Tests](#tests).

---

## License

MIT — see [LICENSE](./LICENSE).
