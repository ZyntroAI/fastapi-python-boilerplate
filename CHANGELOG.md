# Changelog

All notable changes to this repository. Dates are UTC.

Open problems and known blockers are tracked separately in
[`PROBLEMS.md`](./PROBLEMS.md), using the same date sections.

## [2026-09-12]

### Added
- **PR #212** — docs: added `docs/MCP-Guide-Complete.md` (MCP-DOC-2026-0912), a
  Thai-language troubleshooting and setup reference for Model Context Protocol
  servers covering the three most common failure modes: Google Cloud ADC
  (`DefaultCredentialsError`, `gcloud auth application-default login`, quota
  project, service-account path, and an explicit warning not to commit
  credentials), missing runtimes (Node.js / Dart / Go install links, per-shell
  PATH setup, the caveat that GUI MCP clients do not read shell profiles, and
  the `.agent/settings.json` → `mcp/servers.json` config shape), and third-party
  API keys (Antimetal / Lovable / Mobbin / Windsor — safe storage order,
  `.env.example` convention, and how to verify a secret never reached git
  history). Also added `scripts/check-mcp-environment.sh`, an automated checker
  for the same three issues with `--gcp` / `--runtimes` / `--keys` flags and a
  CI-suitable exit code; it never prints secret values, only set/not-set. Linked
  from `docs/README.md`.
- **PR #206** — obsidian: connected the `fastapi-obsidian-backend` deliverable to a
  running Obsidian vault via the Local REST API plugin. Adds `app/obsidian/client.py`
  (vault list/read/write/append/patch/delete, active, JsonLogic + simple search, tags,
  commands, open; injectable transport so the whole surface is testable without a vault)
  and `app/routers/obsidian.py` (`/obsidian` endpoints — reads open, writes require a
  valid JWT **and** `OBSIDIAN_ALLOW_WRITE=1`; unconfigured bridge returns 503). Vault-
  relative paths only: `..`, absolute paths and NUL bytes are rejected with 422 before a
  request is built, and every payload crossing the boundary is passed through the
  CWE-1321 sanitizer (`app/cwe1321_bridge.py`) which strips `__proto__` / `prototype` /
  `constructor` at any depth. Config (`OBSIDIAN_API_URL` / `_API_KEY` / `_ALLOW_WRITE` /
  `_VERIFY_TLS`) is off by default. 33 tests passing. Also records the CI enforcement
  gate in the suite README and `manifest.json`.

## [2026-09-11]

### Added
- **PR #202** — notifications: added `scripts/whatsapp_notify.py` (WhatsApp Cloud API
  client — `test_connection`, `send_message`; env-only config, no secrets in code),
  `tests/test_whatsapp_notify.py` (9 tests, HTTP mocked, incl. `code=100/subcode=33`),
  `docs/notifications/WHATSAPP.md` (secrets setup, endpoint shape, error table), and
  `templates/workflows/notify-whatsapp.yml` (SHA-pinned workflow template, kept outside
  `.github/workflows/` because the App lacks `workflows` permission).
- **PR #193** — docs: added `docs/github-api.md` — a complete GitHub REST v3 +
  GraphQL v4 reference and implementation guide. Covers authentication (PAT,
  GitHub App, installation tokens, a required-scope table), core REST endpoints
  (user, repositories, file contents, issues, pull requests, workflows/Actions)
  with runnable `curl` examples and sample JSON, GraphQL queries/mutations and
  efficient fetching patterns, SDK usage (PyGitHub, `gh` CLI, Octokit), and
  enterprise best practices (rate limits, pagination, error handling, security,
  conditional requests, idempotency). Also added
  `schemas/github-api-schema.json` with example request/response payloads for
  each documented operation.
- **PR #187** — deliverables: added `deliverables/product-crud/` — a full-stack
  Products CRUD reference implementation. Backend is Express + Prisma + Zod in
  five layers (Zod schema → service → controller → routes → mount) with
  pagination, case-insensitive search across `name`/`sku`/`description`, and a
  central error handler returning one shape for `BAD_REQUEST` / `NOT_FOUND` /
  `CONFLICT`. Frontend is Vite + React + TanStack Query, with page, search and
  sort carried in the query key so each page and search term caches separately,
  and `placeholderData: keepPreviousData` so paging dims the table instead of
  flashing a full loading state. 30 tests, no database needed.
  Also ships `docker-compose.yml` (Postgres with a `pg_isready` healthcheck so
  `db:up` can migrate safely), a 30-row idempotent seed script spread across all
  three statuses and deliberately larger than the default page size, and a
  three-stage production `Dockerfile` whose entrypoint applies the Prisma schema
  before starting.

### Fixed
- **PR #189** — deliverables: patched Dependabot alert #101
  (`GHSA-5xrq-8626-4rwp`, `CVE-2026-47429`, critical) in
  `deliverables/product-crud/server/`. `vitest` 2.1.9 → 4.1.11; going to 4.x
  rather than the minimum patched 3.2.6 also clears the separate moderate
  `@vitest/mocker` path-traversal advisory that 3.2.7 still carried. The suite
  is synchronous, `node`-environment and imports only
  `describe`/`expect`/`it`/`vi`/`beforeEach`, so the major bump needed no test
  changes. Also cleared the two moderate prod findings `npm audit` reported
  separately: `express` requires `qs ~6.15.1` and every release in that range is
  affected, so an `overrides` entry pins `qs` to 6.16.0 — the first patched
  release — rather than forcing an `express` major. `npm audit` now reports 0
  vulnerabilities, prod and dev alike.

### Changed
- **PR #191** — chore: moved the root test runner from `jest` to `vitest`
  (`vitest` + `@vitest/coverage-v8`, with `test` / `test:run` / `test:coverage`
  scripts), and added the `vitest.config.mjs` the switch needs. Without a root
  config `vitest run` walks the whole tree and collects
  `deliverables/cwe1321-protection-suite/tests/sanitize.test.mjs` — a
  `node:test` file — then exits 1 with "No test suite found in file"; the config
  scopes collection to the root project and excludes the self-contained
  deliverable packages. Also added `node_modules/` and `coverage/` to
  `.gitignore`, which the repo root had been missing, and committed the first
  root `package-lock.json`.

### Added — Production Docker image (`deliverables/product-crud/server/`)
- **PR #188** — a three-stage `Dockerfile` (`deps` → `build` → `runtime`) for
  the product-crud API, running `node:22-alpine` as non-root (uid 1001) with
  `tini` as PID 1, since the app relies on SIGTERM for its graceful shutdown,
  and a `HEALTHCHECK` against `/health` using Node's global `fetch`. The module
  has no committed `prisma/migrations/`, so the accompanying
  `docker-entrypoint.sh` inspects the filesystem — `migrate deploy` when
  migrations are present, `db push` otherwise — because a bare
  `migrate deploy` would exit 0 having done nothing and leave the container
  reporting healthy with the tables missing. `SCHEMA_SYNC=auto|deploy|push|none`
  overrides it, and a missing `DATABASE_URL` fails fast. `prisma` moved from
  `devDependencies` to `dependencies` so the CLI survives `--omit=dev`.

### Notes
- **PR #190** was closed unmerged as a duplicate of #191: same `jest` → `vitest`
  change to the root `package.json`, opened a minute earlier, but without the
  `vitest.config.mjs` or the `.gitignore` entries, so merging it alone would have
  shipped a `test:run` script that exits 1 on first use.

## [2026-09-10]

### Added
- **PR #169** — deliverables: added `deliverables/pure-agent-dev/` (Issue #63 reference implementation — provider-agnostic Agent on FastAPI; `ComputeProvider` ABC with mock + BytePlus ECS adapters, planner/executor split, DI-based provider selection via `COMPUTE_PROVIDER`, external JSON Schema contract, Docker + compose, 47 tests). The guide's core rule — the Agent must not depend on the BytePlus SDK — is enforced by `tests/test_architecture.py` walking the real import graph, not by convention. All tests run on the mock provider; no cloud credentials needed.
- **PR #170** — docs: recorded PR #169 in this changelog.
- **PR #175** — tasks: added an `archive/` status to the task tracker (`new.inprogress.done/`) as a terminal folder for work closed without shipping (superseded, abandoned, or duplicate), kept outside the `new -> inprogress -> done` flow. `tools/tasks.py` gains the status plus an `ACTIVE_STATUSES` split, and `archive <id> "<reason>"` moves a task and records the reason in its Completion summary.
- **PR #176** — docs: recorded PR #175 in this changelog.
- **PR #168** — chore(workflows): moved 7 non-workflow files (markdown notes and `.yml.txt`) out of `.github/workflows/` into `archive/workflows-junk/`, leaving the directory holding only real workflows.
- **PR #174** — deliverables: added `deliverables/pm-backend/` — a FastAPI app with provider-neutral billing (Stripe / Chargebee / Paddle adapters behind one interface), CSV reconciliation, and sandbox integration tests (58 passed, 15 skipped).
- **PR #178** — deliverables: added `deliverables/agent-core/` — a runnable, tested FastAPI backend for provider-agnostic agent tasks (async `httpx` client, bounded retry + polling, Supabase task store with RLS, `schema.sql`). Ported from the single-file "Dola Core" draft and renamed Dola → Agent. Fixes that made it actually start: lazy settings (import no longer needs credentials), async I/O instead of blocking `requests`, retry that preserves the original error, bounded polling, and a real persistence layer. 25 offline tests.
- **PR #179** — tasks: added `TASK-20260910-005` recording the five things PR #178 could not prove (placeholder base URL, unverified response field names, unapplied Supabase schema, untested RLS, never-run CI example). Also fixed a tracker bug: `TASK_TEMPLATE.md`'s `status:` comment was copied verbatim by `cmd_new`, breaking three tests that read the template.
- **PR #180** — docs: recorded PR #178 and #179 in this changelog.
- **PR #181** — docs: added `PROBLEMS.md` as the companion to this file, tracking open issues and blockers in the same date sections.
- **PR #182** — tasks: closed `TASK-20260910-005` (→ `done/`) with its Completion summary citing both `CHANGELOG.md` and `PROBLEMS.md` P-004. Also corrected two stale records: `TASK-20260910-004` was renamed to match its id and its validation table filled with measured numbers, and `TASK-20260910-003` gained a re-check showing its fix is still not on remote.
- **PR #183** — docs: recorded PR #180–#182 here, added `PROBLEMS.md` P-007 (new-crystalcastle CI reads a `requirements.txt` that does not exist at the root) and P-008 (the `example-task.md` naming bug), and opened `TASK-20260910-006` to own P-007.
- **PR #184** — docs: recorded PR #183 in this changelog.
- **PR #185** — deliverables: added `deliverables/fastapi-obsidian-backend/` — a FastAPI backend for the Obsidian knowledge workflow with six routers (`skills`, `programs`, `billing`, `tools`, `users`, `security`), opt-in encryption at rest, bundled `data/skills/` markdown, and a pinned `requirements.txt`.
- **Commit `de284dc`** (direct, not a PR) — chore: added a root `package.json` for Node tooling (`vercel`, `eslint`/`prettier`, `jest`, `semantic-release`). The same commit carried ~800 files that had accumulated untracked in the working tree — dashboard `.txt` and `.csv` exports, notebook HTML dumps, stray top-level `.py`/`.yml` fragments, and a `.zip`. Flagged in `README.md` under repository health; it has not been reviewed or pruned.

### Fixed
- **Issue #63 closed** — the `pure-agent-dev` implementation merged to `main` via PR #169 (squash `590b8615`); the issue was closed by the PR's `Closes #63` reference. No `.github/workflows/` files were touched, so the merge was not blocked by the App's `workflows` restriction.

## [2026-09-09]

### Added
- **PR #164** — docs: added `deliverables/ai-gateway-architecture-review/` — systematic AI Gateway architecture review focused on resilience & cost control, plus `deliverables/README.md` index update.
- **PR #165** — deliverables: added `deliverables/onspace-ai/` (FastAPI cost+reliability stack — Redis/memory fail-open cache, circuit breaker, fallback router, token budget + context compiler, Prometheus metrics, k8s manifests; 31 tests), `deliverables/manus-client/` (Manus REST API v2 async client on dot-notation endpoints `task.create`/`task.listMessages`; 10 tests), `deliverables/firecrawl-fastapi/` (FireCrawl + FastAPI production scraper/crawler, firecrawl-py <2.0.0 v1.x surface; 6 tests). All no workflow files, runnable via mock/fail-open.
- **PR #155** — scaffold: added the ZyntroAI merged monorepo scaffold as additive (no-clobber) new files — FastAPI/SQLModel async backend (JWT auth, Alembic, Item CRUD, 6 passing tests), React+Vite+TS frontend, Obsidian↔Algolia knowledge indexer, k8s manifests, 6 typed PR templates, and spec docs. No existing main file modified.
- **PR #160** — docs: rewrote `README.md` to reflect the actual repo structure (OAuth2 PKCE FastAPI core, `graphql_api/`, `skills/`, `deliverables/`, `docs/`, `helm/` + `k8s/`, `tests/`), replacing the stale self-referential comparison doc.
- **PR #158** — docs: added root `RELEASE.md` release guide (semantic-versioning policy, release flow, release-drafter auto-label mapping, verification checklist, rollback guidance).
- **PR #156** — docs: filled `SECURITY.md` with a real security policy (supported versions, private-advisory reporting flow, expected-response SLA by severity, repo security practices); added default `.github/PULL_REQUEST_TEMPLATE.md` pointing typed changes to the 6 specialized templates.
- **PR #150** — docs: added `deliverables/gemini-cli-skills/`: research brief on google-gemini/gemini-cli docs & skills architecture, `AGENTS.md` + `SKILLS.md` overlay index, `@zyntroai` skill overlay templates (github/pull-request, coding/typescript, devops/ci-cd, security/secret-scan), canonical `templates/skill-template.ts`.
- **PR #148** — feat(security): added `deliverables/cwe1321-protection-suite/` — CWE-1321 Prototype Pollution Protection Suite: JS rules (ESLint config, Semgrep, CodeQL query, `sanitize.js` utility) + Python rules (Bandit config, Semgrep, `safe_parser.py` FastAPI/Pydantic-safe loader), `manifest.json`, `SKILL.md`, README, test report, and runnable tests (`sanitize.test.mjs` + `test_safe_parser.py`).
- **PR #147** — docs: added dev/prod `.bicepparam` examples (F1 / P1v2) under `deliverables/azure-cli-2026/examples/bicepparam/`.
- **PR #146** — docs: added full Bicep/IaC appendix to `deliverables/azure-cli-2026/azure-cli-2026.md` (`az bicep` build/decompile/lint/publish, standard file structure, sample templates, CLI deploy + what-if + security, GitHub Actions workflow commands); new `docs/README.md` + `deliverables/README.md` indexes; new `docs/github-actions/workflow-commands-reference.md`; new example workflow `deliverables/azure-cli-2026/examples/azure-bicep-deploy.yml`.
- **PR #145** — docs: added Azure CLI 2026 flashcards & one-page cheat sheet to `deliverables/azure-cli-2026/azure-cli-2026.md`.
- **PR #142** — extended `deliverables/notebooklm-access-suite/` to full sub-skill set: validate/guide/link_security/provenance/verify/knowledge (read-only, evidence-based). Suite now 22 tests.
- **PR #140** — added `deliverables/notebooklm-access-suite/`: NotebookLM access-artifact suite core P0 (resolver/access/artifact), evidence-based read-only access classification. 12 tests.
- **PR #138** — added `deliverables/agent-skill-template/`: standard agent-skill template (JSON+YAML), progressive-disclosure loader (`load_skill`/`resolve_layers`/`verify_gates`/`prepare_skill`), NotebookLM filled example. 11 tests.
- **PR #136** — added `deliverables/notebooklm-link-share/`: NotebookLM link-share skill (`notebooklm_link_share`), normalize/validate/share-templates, pure stdlib, SKILL.yaml. 9 tests.
- **PR #134** — added `runpod_client.py` to `deliverables/agent-security-suite/`: RunPod client (lazy import), ACTION_SCHEMA validation, audit hook, `connect_runpod()`. Suite now 28 tests.
- **PR #132** — added `ci_ops` module to `deliverables/agent-security-suite/`: permission-aware checks (contents:write ≠ workflows:write), SHA-pin scan, CI root-cause fingerprint. Suite now 21 tests.
- **PRs #125–#130** — Dependabot: docker base bumps (alpine 3.24, node 26, python 3.14), npm (vercel), pip (production-deps), npm dev-deps.
- **PR #122** — extended `deliverables/agent-security-suite/`: LangGraph time-travel recovery (`recovery.py`) + MCP client (`mcp_client.py`), lazy-imported (core runs without them). Now 11 tests.
- **PR #120** — `deliverables/agent-security-suite/`: runnable core (ISO-27001-style SQLite audit log with SHA-256 payload hash, JSON-schema validation, stdlib-only Slack alert). 7 tests.
- **PR #118** — `skills/research/`: multi-source knowledge synthesis (ResearchSkill.run) built on fetching — dedupe, cross-validation to 0.0–1.0 confidence, contradiction flags, provenance graph + checksum. 7 tests.
- **PR #116** — `skills/fetching/` extended with async GraphQL (`clients/graphql.py`, TTL cache) and WebSocket (`clients/websocket.py`, wss/ws, lazy `websockets`) clients; `ssrf.check_ws()`. Now 17 tests.
- **PR #114** — `skills/fetching/`: SSRF-safe async HTTP fetch skill (httpx) with retry + TTL cache + provenance; SSRF guard blocks private/local/metadata hosts; GitHub source. 9 tests.
- **PR #112** — Reference deliverables under `deliverables/`: GitHub DevOps Toolkit (PR templates, SHA-pinned gatekeeper workflows, externalized branch-protection config, Terraform module) + AI Agents Decision Pack (comparison matrix, Notion/Figma/Miro assets). Docs/config only.

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
- CI on this repo is red at the "Set up job" step from the org's SHA-pin policy: a job refuses to start when a referenced action is not pinned to a full commit SHA. Measured on **2026-09-10**, `main`'s workflows still mix full SHAs with mutable tags — `actions/checkout@v4` (17 refs), `actions/upload-artifact@v4` (6), `actions/setup-python@v5` (7), `subosito/flutter-action@v2` (5), `somaz94/compress-decompress@v1` (5), `gitleaks/gitleaks-action@v2`, and others.
- The SHA-pin fix requires writing `.github/workflows/`, which the Fig GitHub App is not permitted to do (pushes are rejected with `refusing to allow a GitHub App to create or update workflow ... without workflows permission`). It must therefore be applied by a maintainer, or with elevated App permissions. This is why feature PRs on this repo show red checks even when their own tests pass.
