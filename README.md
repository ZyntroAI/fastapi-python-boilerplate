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

## Documentation

- `docs/` — API, GraphQL, and reference guides.
- `deliverables/` — each suite ships its own README, SKILL.md, and tests.

## License

See [LICENSE](./LICENSE).
