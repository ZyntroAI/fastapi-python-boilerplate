# Agent Core

A self-contained, runnable FastAPI backend for **provider-agnostic agent tasks**:
submit a task, poll it to completion, persist the history. Every layer is a
separate module and every risky behaviour is tested.

Ported from a single-file "Dola Core" draft and reworked into something that
actually runs: **Dola → Agent**, blocking `requests` → `httpx`, eager settings →
lazy settings, and an unbounded poll loop → a bounded one.

## Modules

| File | Responsibility |
| --- | --- |
| `agent_core/config.py` | Lazy, typed settings (import never needs credentials) |
| `agent_core/base.py` | `TargetClient` ABC + terminal-status set |
| `agent_core/client.py` | Async HTTP client, auth, error mapping |
| `agent_core/errors.py` | Exception hierarchy |
| `agent_core/retry.py` | Bounded retry with exponential backoff |
| `agent_core/polling.py` | Bounded task polling |
| `agent_core/schemas.py` | Pydantic models for validation + OpenAPI |
| `agent_core/db.py` | Supabase task store (PostgREST over httpx) |
| `agent_core/api.py` | FastAPI routes + app factory |
| `schema.sql` | `agent_tasks` table, RLS policy, index |

## What changed from the original draft

The draft was labelled "ready for production" but would not have started:

- **Settings were built at import time** with required fields, so `import
  dola_core` raised `ValidationError` without a full `.env` — including under
  `pytest`. Now `get_settings()` is lazy and cached.
- **`requests` (blocking) inside `async def`** froze the whole event loop for
  every request. Now `httpx.AsyncClient`, one pooled client per request.
- **The retry decorator swallowed the real error**, ending in a generic
  `RuntimeError`. Now the original `AgentAPIError`/`AgentRateLimitError`
  propagates once the budget is spent, and 4xx is never retried.
- **`poll_task` had no timeout** — a task stuck in `running` hung the request
  forever. Now `AgentPollTimeoutError` after `AGENT_POLL_TIMEOUT`.
- **`result()` had no retry** while its siblings did. Now consistent.
- **The SQL was an unused string** and there was no DB code at all. Now
  `schema.sql` is applied for real and `TaskStore` is a working repository.
- **The CI example used tag refs** (`actions/checkout@v4`), which this org's
  SHA-pinning policy rejects. The example pins full SHAs.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # fill in AGENT_API_KEY
pytest -q                      # 25 tests, no network, no credentials
```

Library mode:

```python
from agent_core import AgentClient, poll_task

async with AgentClient() as client:
    task_id = await client.submit({"prompt": "hello"})
    task = await poll_task(task_id, client)
    print(task.status, task.result)
```

Service mode:

```bash
uvicorn agent_core.api:app --host 0.0.0.0 --port 8000
```

Then `/docs`, `/health`, `POST /api/agent/submit`,
`GET /api/agent/status/{task_id}`, `GET /api/agent/result/{task_id}`.

## Container

The `Dockerfile` builds a slim, non-root runtime. The base image is pinned by
digest so builds are reproducible, and only `agent_core/` and
`requirements.txt` enter the context — tests, charts and docs stay out.

```bash
docker build -t zyntroai/agent-core:1.0.0 .
docker run --rm -p 8000:8000 \
  -e AGENT_API_KEY=... \
  zyntroai/agent-core:1.0.0
```

The image runs as uid `10001`, and its `HEALTHCHECK` probes `/health` with the
interpreter already in the image (no `curl` added). Verified locally: `/health`
returns `{"ok":true,"provider":"agent","version":"1.0.0"}` and `/docs` returns 200.

## Kubernetes (Helm)

`charts/agent-core/` deploys the same image with production defaults:

```bash
helm upgrade --install agent-core charts/agent-core \
  --namespace agent-core --create-namespace \
  --set secrets.existingSecret=agent-core-secrets
```

What the chart gives you by default:

- **Non-root and locked down** — `runAsNonRoot`, uid `10001`, `seccompProfile:
  RuntimeDefault`, `allowPrivilegeEscalation: false`, all capabilities dropped,
  and `readOnlyRootFilesystem: true` with an `emptyDir` mounted at `/tmp`.
- **Credentials out of values** — pass `secrets.existingSecret` (or sync from a
  secrets manager). Only if you leave it empty *and* set values does the chart
  create a Secret; otherwise it renders none and the NOTES tell you what the
  Deployment expects.
- **Probes** on `/health` for both liveness and readiness, plus a config
  checksum annotation so a config change rolls the pods.
- **Image pinning** — `image.digest` wins over `image.tag`; both default away
  from `latest`.

| Value | Default | Notes |
| --- | --- | --- |
| `replicaCount` | `2` | Ignored when `autoscaling.enabled` |
| `image.tag` | chart `appVersion` | Pin a version or set `image.digest` |
| `secrets.existingSecret` | `""` | Preferred over inline values |
| `service.port` | `8000` | ClusterIP |
| `ingress.enabled` | `false` | |
| `autoscaling.enabled` | `false` | CPU target 75% |
| `resources.requests` | `100m` / `128Mi` | limits `1` / `512Mi` |

Validated with `helm lint` (clean) and `helm template` across the secret,
digest, ingress and HPA paths — all seven objects render as intended.

## Configuration

| Variable | Default | Notes |
| --- | --- | --- |
| `AGENT_PROVIDER` | `agent` | Reported by `/health` |
| `AGENT_BASE_URL` | `https://api.agent.ai/v2` | Provider endpoint |
| `AGENT_API_KEY` | — | Required to call the provider |
| `AGENT_TIMEOUT` | `120` | Per-request seconds |
| `AGENT_MAX_RETRIES` | `3` | Attempts per call |
| `AGENT_POLL_INTERVAL` | `2` | Seconds between status checks |
| `AGENT_POLL_TIMEOUT` | `300` | Polling budget |
| `SUPABASE_URL` | — | Needed only for persistence |
| `SUPABASE_SERVICE_KEY` | — | Server-side only |

Secrets stay in the environment or a secrets manager. `.env` is gitignored.

## Security

- The API key travels in an `Authorization` header, never a query string.
- `schema.sql` enables **Row Level Security** and scopes every row to
  `auth.uid() = user_id`, so one tenant cannot read another's tasks.
- `SUPABASE_SERVICE_KEY` is server-side only; it is never sent to a client.
- Tests run fully offline against `httpx.MockTransport` — no real key, no
  outbound call.

## Tests

25 tests covering: auth header, 401/429/5xx mapping, retry backoff timing,
retry exhaustion preserving the original error, missing-key behaviour,
timeout mapping, poll terminal states, poll timeout, every HTTP route,
dependency-override error paths, settings validation, and the task store
(save/get/upstream error).

Markers: all async tests run under `pytest-asyncio` in `asyncio_mode = auto`.
