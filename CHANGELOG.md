# Changelog

All notable changes to this repository. Dates are UTC.

## [2026-09-10]

### Added
- **PR #169** — deliverables: added `deliverables/pure-agent-dev/` (Issue #63 reference implementation — provider-agnostic Agent on FastAPI; `ComputeProvider` ABC with mock + BytePlus ECS adapters, planner/executor split, DI-based provider selection via `COMPUTE_PROVIDER`, external JSON Schema contract, Docker + compose, 47 tests). The guide's core rule — the Agent must not depend on the BytePlus SDK — is enforced by `tests/test_architecture.py` walking the real import graph, not by convention. All tests run on the mock provider; no cloud credentials needed.
- **PR #170** — docs: recorded PR #169 in this changelog.
- **PR #175** — tasks: added an `archive/` status to the task tracker (`new.inprogress.done/`) as a terminal folder for work closed without shipping (superseded, abandoned, or duplicate), kept outside the `new -> inprogress -> done` flow. `tools/tasks.py` gains the status plus an `ACTIVE_STATUSES` split, and `archive <id> "<reason>"` moves a task and records the reason in its Completion summary.

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
