# Changelog

All notable changes to this repository. Dates are UTC.

## [2026-09-08] — Skill-native architecture, secrets cleanup, and GraphQL API

### Added — GraphQL API (`graphql_api/`, self-contained subproject)
- **PR #107** — Integrated a self-contained FastAPI + Strawberry GraphQL service under `graphql_api/` (JWT auth, `me`/`users` cursor-paginated queries, `login`/`create_user` mutations, subscription scaffold, async SQLAlchemy, `/health`, Dockerfile + compose).
- **PR #109** — DB-backed resolvers + Alembic migrations: async CRUD (`crud.py`, bcrypt hash/verify), initial migration creating the `users` table, resolvers reading/writing the database.
- **PR #110** — Redis pub/sub subscriptions (real `user_created` event + publish on `create_user`), `@cache_resolver` decorator utility, standardized GraphQL errors (`PermissionDenied`/`AuthenticationRequired`/`ResourceNotFound` with `code`/`status` extensions).

### Added — Central credential management + workflow guardian
- **PR #104** — `app/core/credential_broker.py` (thin async broker client, metadata-only, tolerates an unconfigured broker), `app/skills/credential_management` + `workflow_guardian` client wrappers, `credentials/registry.yaml` (references only), `requirements/skills.txt`.

### Changed — Security & config fixes
- **PR #105** — Untracked `.env` (was committed with real secrets despite `.gitignore`); added safe `.env.example` (placeholder/vault references) + `vault/` policy and app-role.
- **PR #106** — Fixed `app/config.py` (used `BaseSettings` without importing it) and `tests/conftest.py` (used `AsyncGenerator`/`app`/`get_current_user` without importing them).

### Notes
- Earlier `CHANGELOG.md` content describing a "Claude REST API ecosystem" described files not present in this repository; it has been replaced with this accurate record.
- CI on this repo is red at the "Set up job" step from the org's SHA-pin policy (workflow actions must be pinned to full commit SHAs). A SHA-pin fix for all workflow files is prepared on branch `fix/sha-pin-all-workflows` and awaits admin grant of the GitHub App's `workflows` permission to push.
