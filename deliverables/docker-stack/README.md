# Docker stack

A working container stack for this repo: **FastAPI + PostgreSQL + Redis**, with
an optional nginx front end.

The repo-root `Dockerfile` is a Node.js image (`FROM node:26-alpine`, `EXPOSE
4000`, `CMD ["node","dist/index.js"]`) — it does not build this application, and
the root `docker-compose.yml` expects a `backend/` build context that is not
this app. Both are left untouched; this folder is additive.

```
deliverables/docker-stack/
├── Dockerfile                 multi-stage Python image (app.main:app)
├── .dockerignore              trims the large repo context
├── docker-compose.yml         api + postgres + redis (+ optional nginx)
├── requirements.stack.txt     the 2 deps the app needs beyond requirements.txt
├── Makefile.docker            docker-build / up / smoke / test targets
├── .env.stack.example         env template
└── nginx/nginx.conf           reverse proxy for the `proxy` profile
```

## Quick start

```bash
# from the repo root
cp deliverables/docker-stack/.env.stack.example .env

make -f deliverables/docker-stack/Makefile.docker docker-up
make -f deliverables/docker-stack/Makefile.docker docker-smoke
make -f deliverables/docker-stack/Makefile.docker docker-down
```

Or with compose directly:

```bash
docker compose -f deliverables/docker-stack/docker-compose.yml up --build
```

| Endpoint | URL |
| --- | --- |
| API root | http://localhost:8000/ |
| Health | http://localhost:8000/health |
| Readiness | http://localhost:8000/health/ready |
| Liveness | http://localhost:8000/health/live |
| OpenAPI | http://localhost:8000/docs |

## Two things the repo did not tell us

**1. `requirements.txt` is not enough to start the app.** Building a clean venv
from it and importing `app.main` fails. Two packages are imported but never
declared:

| Module | Missing package | Imported by |
| --- | --- | --- |
| `pydantic_settings` | `pydantic-settings` | `app/core/config.py`, `app/config.py` |
| `jwt` | `pyjwt` | `app/services/token_service.py` |

`requirements.stack.txt` adds them. It is additive — `requirements.txt` at the
root is not modified, so CI installs exactly what it installed before. Found
with `scripts/probe_deps.py`, which walks the import chain in a throwaway venv
rather than guessing.

**2. The health path is `/health`, not `/health/`.** `/health/` answers with a
**307 redirect**, and `curl -f` counts 3xx as success — so a `HEALTHCHECK` on
`/health/` would report `healthy` while proving nothing. Every probe in this
folder (Dockerfile, compose, Makefile, nginx) uses the exact path.

Verified with FastAPI's `TestClient`:

```
/health            -> 200
/health/           -> 307
/health/ready      -> 200
/health/live       -> 200
```

## Environment

`DATABASE_URL` is the one worth reading. `app/config.py` defaults it to a local
sqlite file (`sqlite+aiosqlite:///./dev.db`); the stack points it at the
`postgres` service so the containers are actually wired together.

Two settings modules disagree on the JWT variable name — `app/core/config.py`
reads `JWT_SECRET`, `app/config.py` reads `JWT_SECRET_KEY`. The compose file
sets **both** from one `${JWT_SECRET}` value, so whichever module loads gets a
real secret instead of falling through to the `super-secret-change-in-production`
default. That default is fine for a laptop, not anywhere else.

## What is verified, and what is not

**Verified here:**

- the compose file parses and declares `api`, `postgres`, `redis`, `proxy`
- `requirements.txt` + `requirements.stack.txt` produce an environment where
  `import app.main` succeeds (clean venv)
- all four health paths return the status codes listed above (`TestClient`)
- every env var the compose file sets is one the app actually reads

**Not verified — no Docker daemon in this environment:**

- the image has never been built
- the stack has never been run end to end
- the `proxy` profile's nginx config has never been loaded

Treat the first `docker compose up --build` as the real test. The Dockerfile is
two-stage with a non-root user, `tini` as PID 1, and a `HEALTHCHECK` on `/health`.

## Ports and volumes

`API_PORT` (default 8000) and `PROXY_PORT` (default 8080). PostgreSQL and Redis
have no host port mapped — reach them with
`docker compose exec postgres psql -U app -d appdb`.

Named volumes `postgres-data` and `redis-data` persist across restarts.
`make docker-clean` removes them too, which deletes the database.
