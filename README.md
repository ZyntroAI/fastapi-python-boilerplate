# FastAPI Python Boilerplate — AI-Driven

An opinionated FastAPI monorepo/boilerplate used by ZyntroAI as the foundation for production AI services, agent tooling, and reference documentation. The repo is a working collection: an OAuth2 PKCE API core, a GraphQL layer, a library of reusable AI-agent skills, packaged deliverable suites, and extensive docs.

> This README reflects the repository as it stands. Individual suites carry their
> own READMEs with deeper detail.

## What's inside

| Path | Purpose |
| ---- | ------- |
| `app/` | FastAPI application core (`main.py`, routers under `api/`, core config, services) |
| `graphql_api/` | GraphQL service layer (Strawberry) |
| `main.py` | OAuth2 PKCE API entrypoint (`/auth`, `/callback`, `/health`) |
| `frontend/` | React + Vite + TypeScript frontend (own `package.json`, `Dockerfile`, `tsconfig.json`) |
| `skills/` | Reusable AI-agent skill definitions (e.g. `fetching`, `changelog-auto-update`, `credential-management`) |
| `deliverables/` | Self-contained feature suites, each with its own README, tests, and CI (e.g. `pure-agent-dev`, `cwe1321-protection-suite`, `onspace-ai`, `firecrawl-fastapi`, `manus-client`, `notebooklm-access-suite`, `agent-security-suite`, `azure-cli-2026`, `agent-skill-template`, `product-crud`, `fastapi-obsidian-backend`, …) |
| `docs/` | Reference & knowledge documentation (GraphQL, FireCrawl, Google Chat, GitHub Actions, incident drills) |
| `helm/` | Helm charts (OAuth app) |
| `k8s/` | Kubernetes manifests |
| `tests/` | Test suite (`tests/` + per-suite tests) |
| `.github/workflows/` | CI/CD, release drafter, auto-merge, secret-scan, coverage |

## Quick start

```bash
# create .env from the example, then:
docker compose up -d --build
# or run directly:
pip install -r requirements.txt
uvicorn main:app --reload
```

- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- The React frontend in `frontend/` runs separately (`npm install && npm run dev`).
- Every suite under `deliverables/` is self-contained: see its own README. Several ship a `docker-compose.yml` and a seed script, so a fresh clone is one command from a running stack (e.g. `deliverables/product-crud/`).

## Stack

- **FastAPI** (async, auto OpenAPI) + **Pydantic v2**
- **LangGraph / LangChain** + **OpenAI** for agent workflows
- **Strawberry GraphQL** (`graphql_api/`)
- Redis / PostgreSQL integrations under `app/integrations`
- Docker + docker-compose, Helm/K8s for deployment

## Repository health & standards

- Secret scanning, coverage, and a test suite run in CI.
- **CI status:** jobs currently fail at the *Set up job* step because the org's SHA-pin policy rejects workflows that reference actions by mutable tag (e.g. `actions/checkout@v4`). A PR's own tests passing locally does not turn its checks green. Fixing this needs write access to `.github/workflows/`, which the automation App does not have — see the 2026-09-08 notes in `CHANGELOG.md`.
- External-service failures fail open (graceful degradation).
- **Root Node tooling is declared but not wired up.** `package.json` lists `vercel`, `eslint`/`prettier`, `jest` and `semantic-release`, but there is no lockfile at the root, no `eslint.config.*` (so `npm run lint` fails against ESLint 10, which requires the flat config file), and `scripts.vite` holds a version range where a command belongs. With no lockfile the root dependency tree has also never been scanned for advisories. Treat this as present but unverified rather than as a working build path.
- **The repository root carries a large volume of unreviewed files** (~800, added in `de284dc`): dashboard exports, notebook HTML dumps, loose scripts and archives mixed in with the source tree. It has not been pruned or classified.
- Secrets live only in environment / CI secrets — never in source.
- See `SECURITY.md` (reporting), `CONTRIBUTING.md` (PRs), `RELEASE.md` (releases).

## 📌 แผนการพัฒนา (Roadmap)

- [ROADMAP.md](./ROADMAP.md) — แผนงาน 8 เฟส + Milestone M4 (`Merge → Stabilize → Integrate → Build`)
- [TASKS.md](./TASKS.md) — รายการงานที่ตรวจสอบได้

## Documentation

- `docs/` — API, GraphQL, and reference guides.
- `deliverables/` — each suite ships its own README, SKILL.md, and tests.

## CI/CD & supply-chain integrity

The repository's supply-chain policy is **full-SHA pinning**: every `uses:` reference
must point at a 40-character commit SHA, never a mutable tag such as `@v4`. The org's
policy gate refuses a workflow that references an action by tag.

**Current state (2026-09-12) — verified against `main`:**

- A minority of references are already SHA-pinned; the majority are still tags
  (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
  `github/codeql-action/*@v3`, `docker/*` and others).
- Six workflow files are not valid YAML as committed, so they never run:
  `ci.yml`, `secret-scan.yml`, `Auto-Index-Sync.yml`, `dependabot-automerge.yml`,
  `test-suite.yml`, and `github-actions-autodebug-autorerun` (which also has no
  `.yml`/`.yaml` extension).
- Because jobs cannot start, a feature PR shows red checks even when its own
  tests pass locally. See the 2026-09-08 notes in [`CHANGELOG.md`](./CHANGELOG.md)
  and [`PROBLEMS.md`](./PROBLEMS.md).

**Reference SHAs** (tags resolved to commits, 2026-09-12) for the actions used by
`ci.yml`:

```yaml
uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262        # v4
uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065    # v5
uses: codecov/codecov-action@b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238  # v4
uses: github/codeql-action/init@faaca9a8f6edddba5725ffe5adefdab6669a2eca     # v3
uses: github/codeql-action/analyze@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9     # v3
uses: docker/build-push-action@ca052bb54ab0790a636c9b5f226502c73d547a25 # v5
```

Fixing this requires write access to `.github/workflows/`, which the automation App
does not hold — it must be applied by a maintainer or with elevated App permissions.
See [`SECURITY.md`](./SECURITY.md) for the policy and how to report a supply-chain
issue.

## License

See [LICENSE](./LICENSE).
