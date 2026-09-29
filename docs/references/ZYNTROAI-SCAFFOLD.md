# ZyntroAI — Merged Monorepo Scaffold (Proposal)

> **Status: PROPOSAL / PR for review** — additive, no-clobber addition to the
> repo. Does not replace or modify any existing file. See `FILE-MANIFEST.md`
> for the full inventory and the colliding-names list.

Unified architecture across backend, frontend, knowledge indexing, Kubernetes
and CI/CD — presented as a ready-to-review scaffold so nothing existing is
overwritten before you decide what to adopt.

Generated: 2026-09-09 · Python 3.11 · FastAPI · React · PostgreSQL · Redis · K8s · GitHub Actions

## What this PR adds

| Area | Path | Contents |
|---|---|---|
| Backend (Python) | `backend/` | FastAPI + SQLModel async API, Alembic migrations, Pydantic config, JWT auth, pytest suite (6 passing) |
| Frontend | `frontend/` | React + Vite + TypeScript shell with type-safe API client |
| Knowledge | `knowledge/` | Obsidian REST API client + Algolia indexer (`diff_policy.py`, `push_index.py`) |
| Kubernetes | `k8s/` | Backend/frontend Deployments, Services, Ingress, HPA, Secrets (helm chart untouched) |
| CI/CD | `.github/workflows/` | `pr-ci.yml` (type classify → reusable validation → tests) + `pr-validation.yml` |
| Docs | `README.md`, `FILE-MANIFEST.md` | This spec + machine-readable inventory |

> **Note:** `docker-compose.yml` and `.env.example` already existed on `main`;
> this PR intentionally does **not** overwrite them (see
> `FILE-MANIFEST.md` → "Collisions — left untouched").

## Backend core

`backend/app/core/config.py` — type-safe env via pydantic-settings.
`backend/app/core/security.py` — bcrypt hashing + JWT (python-jose).
`backend/app/infrastructure/db.py` — async SQLModel engine + sessions.
`backend/app/api/deps.py` — `get_db` + JWT `get_current_user`.
`backend/app/main.py` — lifespan, CORS, exception handler, `/health`.
`backend/app/api/v1/...` — `models/item.py`, `schemas/item.py`,
`services/item_service.py`, `routes/items.py` (full CRUD data path).

### Verify

```bash
cd backend
pip install -e ".[dev]"     # or: pip install fastapi sqlmodel ... pytest
pytest tests/ -v            # 6 passing
```

## CI/CD workflow

- `.github/workflows/pr-ci.yml` — `pull_request` + `push` to `main`; classifies
  the PR type from its body, calls the reusable validator, runs backend lint +
  tests, and syncs the knowledge index on Docs PRs / `main`.
- `.github/workflows/pr-validation.yml` — reusable `workflow_call`: title
  format (Conventional Commits), template completeness, checklist scan, secrets
  scan (Gitleaks), Ruff, TS build, and type-gated dependency/markdown/release
  checks. Emits a `validation_result` output for branch protection.

## Next steps

1. Review this PR's additions (everything is **new**; nothing existing changed).
2. Decide which areas to adopt (e.g. keep the new `backend/` Python app
   separate from the existing root `app/`, or reconcile them).
3. Set branch protection to require `validate / validation_result` + 1 approval.
4. Add secrets: `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY`, `OBSIDIAN_API_TOKEN`,
   `GITHUB_TOKEN`.
