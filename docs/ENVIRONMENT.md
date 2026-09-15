# Environment configuration

How this repository organizes environment variables, and which file owns what.

The problem this solves: `.env` used to be committed at the root while the
codebase reads **148 distinct variables** across its components. A single
tracked file could not document them, and it leaked credentials. Now every
component carries a `.env.example` beside its code, `.env` is ignored
everywhere, and this page is the index.

`.env.example` files are **documentation**. They contain placeholders only,
they are tracked on purpose, and they are the file a new contributor copies:

```bash
cp .env.example .env            # core app
cp graphql_api/.env.example graphql_api/.env
```

---

## 1. Layout — which file belongs to which component

| Template | Component | Consumed by |
|---|---|---|
| `.env.example` | Core FastAPI app | `app/core/main.py`, `app/core/config.py`, `app/config.py`, `docker-compose.yml` |
| `graphql_api/.env.example` | GraphQL API | `graphql_api/app/config.py`, `graphql_api/docker-compose.yml` |
| `frontend/.env.example` | Vite frontend | `frontend/src/lib/api.ts` |
| `scripts/.env.example` | Operational scripts | `scripts/whatsapp_notify.py`, `scripts/push_index.py`, `scripts/kube-cost-check.py` |
| `deliverables/pm-backend/.env.example` | Program Management backend | `deliverables/pm-backend/app/config.py` |
| `deliverables/fastapi-obsidian-backend/.env.example` | Obsidian backend | `deliverables/fastapi-obsidian-backend/app/{config,security,user_store}.py` |
| `deliverables/agent-security-suite/.env.example` | Agent security suite | `agent_security_suite/{config,runpod_client}.py` |
| `deliverables/manus-client/.env.example` | Manus API client | `manus_client/cli.py` |
| `deliverables/product-crud/server/.env.example` | product-crud API server | Prisma (`schema.prisma`), `server/src/{index,app}.ts` |
| `deliverables/product-crud/web/.env.example` | product-crud web client | `web/src/lib/api.ts`, `web/vite.config.ts` |
| `deliverables/agent-core/.env.example` | Agent-core deliverable | `deliverables/agent-core` |
| `deliverables/fig-best-practices/examples/broken-project/.env` | **Fixture, tracked on purpose** | The quality gate's SECURITY check — see §6 |

### Things that are intentionally *not* templated

- **CI secrets** (`.github/workflows/**`) are set in repository settings, not
  in files. §5 lists them.
- **The `tests/` suite** reads `API_BASE_URL` (and the compose `POSTGRES_*` /
  `DATABASE_URL` / `REDIS_URL`) from the calling environment —
  `tests/docker-compose.yml` and CI supply them.
- **`k8s/`, `helm/`, `docker/`** carry their own manifests where values are
  injected by the platform.

---

## 2. Precedence — what wins

Every loader in this repo follows the same order, highest priority first:

1. **Real environment variables** already exported in the shell / CI job.
2. **`.env`** in the component directory (only fills keys that are *not*
   already set — `pm-backend`'s loader skips existing keys explicitly).
3. **Code defaults** in the settings class.

Two consequences worth knowing:

- Setting a variable in the shell always beats the file, so a stray `.env`
  cannot silently override CI.
- `pydantic-settings` classes (`app/core/config.py`, `graphql_api/app/config.py`)
  declare `extra = "ignore"`, so unrelated keys in your local `.env` are fine.
  Do not remove that — without it, `Settings()` raises at import.

---

## 3. Variable reference — core app

Read by `app/core/main.py` and `app/core/config.py`.

| Variable | Default | Notes |
|---|---|---|
| `ENV` | `local` | `local` \| `vercel` \| `production`. Selects the OAuth callback and frontend URL. |
| `APP_NAME` | `ZyntroAPI` | Shown in OpenAPI metadata. |
| `APP_VERSION` | `0.1.0` | Shown in `/health` and OpenAPI. |
| `LOG_LEVEL` | `INFO` | |
| `PORT` | `8000` | |
| `DEBUG` | `true` | |
| `FRONTEND_ORIGIN` | — | Single-origin CORS fallback. |
| `FRONTEND_ORIGINS` | — | Comma-separated; **wins** over `FRONTEND_ORIGIN` when set. |
| `JWT_SECRET` | `super-secret-change-in-production` | **Must** be replaced in production. Read by `app/core/config.py`. |
| `JWT_SECRET_KEY` | `super-secret-change-in-production` | **Must** be replaced in production. Read by `app/config.py`. |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRE_MINUTES` | `60` | |
| `OAUTH_CLIENT_ID` | `""` | OAuth flows validate at use, not import. |
| `OAUTH_CLIENT_SECRET` | — | Optional — the PKCE callback does not need one. |
| `OAUTH_AUTHORIZE_URL` / `OAUTH_TOKEN_URL` / `OAUTH_USERINFO_URL` | Google endpoints | Override for another provider. |
| `DATABASE_URL` | — | Use `postgresql+asyncpg://`. |
| `REDIS_URL` | — | Optional; token storage falls back to memory. |
| `CREDENTIAL_BROKER_URL` / `BROKER_TOKEN` | — | Broker is metadata-only; no raw secrets. |
| `SLACK_AST10_WEBHOOK` | — | Alert webhook (`app/integrations/slack.py`). |
| `SENTRY_DSN` | — | Error reporting. Unset disables Sentry. |
| `CACHE_ENABLED` | `true` | Toggle the cache layer. |
| `CACHE_TTL` | `300` | Cache entry lifetime, seconds. |
| `BYTEPLUS_ACCESS_KEY` / `BYTEPLUS_SECRET_KEY` / `BYTEPLUS_REGION` | — | Provider keys. |

`docker-compose.yml` additionally substitutes `DB_PASSWORD`,
`MINIO_PASSWORD` and `GRAFANA_PASSWORD` for its service defaults.

Finally, the root template carries a **Reserved** block (`VAULT_ADDR`, `VAULT_ROLE`, `ALERT_SLACK_WEBHOOK`). No code in this repo
reads them yet — they are placeholders for the broker/Vault rollout, and
setting them today has no effect.

---

### Two settings modules, one `.env`

The core app has **two** settings classes that both load `.env`, and they do
not declare the same fields:

| Module | JWT variable | Imported by |
|---|---|---|
| `app/core/config.py` | `JWT_SECRET` | `app/services/token_service.py` |
| `app/config.py` | `JWT_SECRET_KEY` | `app/core/security.py`, `env.py`, several tests |

They read the *same* `.env` file but different keys. If you set only one, the
encoder and the verifier disagree and every token fails with a 401 — a
confusing symptom, because login itself succeeds. Set **both to the same
value**. Both ship the same insecure dev default, so leaving both unset works
locally; only one set does not.

---

## 4. Networking rule — service name vs localhost

This is the most common local-setup mistake.

| Where the app runs | Host to use |
|---|---|
| Inside docker-compose | the **service name** — `postgres`, `redis` |
| On the host machine | `localhost` + the published port |

So `DATABASE_URL=...@postgres:5432/...` works inside a container and
`...@localhost:5432/...` works from your shell. The templates default to
`localhost` because a copied `.env` starts on the host; compose overrides them.

---

## 5. Secrets policy

**Never commit** a filled-in `.env`. The ignore rules cover `.env` and every
`.env.*` variant, and the negation list re-allows templates:

```gitignore
.env
.env.*
!.env.example
!.env.local.example
!.env.sample
!.env.template
!**/.env.example
```

Those negations are load-bearing: without them `.env.*` silently swallows
every per-component `.env.example`, so the template exists on your disk, `git
status` stays clean, and the change never makes it into the commit. Verify any
template is actually trackable with:

```bash
git check-ignore -v --no-index path/to/.env.example   # prints nothing = good
```

### CI secrets

Set these in **Settings → Secrets and variables → Actions**. Workflows
reference them as `secrets.*`:

- `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY`
- `GITHUB_TOKEN` (provided automatically)
- Firebase: `FIREBASE_ANDROID_APP_ID`, `FIREBASE_SERVICE_ACCOUNT`
- Android signing: `ANDROID_KEYSTORE`, `ANDROID_KEYSTORE_PASSWORD`,
  `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`
- iOS signing: `IOS_P12_CERTIFICATE`, `IOS_P12_PASSWORD`
- Apple: `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_SPECIFIC_PASSWORD`,
  `APPLE_DEVELOPER_ID`, `APPSTORE_API_KEY_ID`, `APPSTORE_ISSUER_ID`,
  `APPSTORE_API_PRIVATE_KEY`

Set them with:

```bash
gh secret set ALGOLIA_API_KEY --repo <owner>/<repo>
```

---

## 6. The one tracked `.env`

`deliverables/fig-best-practices/examples/broken-project/.env` is a **test
fixture**. Its directory re-includes it deliberately:

```gitignore
!.env
```

`deliverables/fig-best-practices/tests/test_gate.py` asserts that the quality
gate flags a committed `.env`, and the fixture's values are inert placeholders
so no scanner mistakes it for a real leak. Removing it would turn a passing
test into a vacuous one. Leave it alone.

---

## 7. Verifying a component's environment

```bash
# Which variables does this app actually read?
grep -rhoE 'os\.getenv\("[A-Z_]+' app/ | sort -u

# Is a template still trackable?
git check-ignore -v --no-index graphql_api/.env.example

# Pre-flight the database / cache wiring before a deploy
python scripts/validate_ci_env.py
```

`scripts/validate_ci_env.py` checks variable presence plus live connectivity to
Postgres and Redis, and prints a suggestion for each failure.
