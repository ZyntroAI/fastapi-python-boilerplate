# syntax=docker/dockerfile:1.7
#
# FastAPI Python Boilerplate — application image
#
# Build context is the REPO ROOT (not this folder), because the app package
# lives at app/ in the root:
#
#   docker build -f deliverables/docker-stack/Dockerfile -t fastapi-app .
#
# The root Dockerfile is a Node.js image and does not build this repo.

# ─── Stage 1: build wheels ────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Build tooling for any sdist that needs compiling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# The repo keeps runtime deps in requirements.txt at the root (CI installs from
# here). Copy them alone first so the dependency layer caches independently of
# application code.
#
# requirements.stack.txt adds the two packages app/ imports but the root file
# does not declare (pydantic-settings, pyjwt) — without them the container
# crashes on `import app.main`. It is additive; the root file is untouched.
COPY requirements.txt ./
COPY deliverables/docker-stack/requirements.stack.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt -r requirements.stack.txt \
    && rm -f requirements.stack.txt

# ─── Stage 2: runtime ─────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENV=production \
    PORT=8000

# curl backs the HEALTHCHECK; tini reaps zombies and forwards signals so
# `docker stop` shuts uvicorn down cleanly instead of waiting for SIGKILL.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Application code. The app package imports as `app.main:app`.
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser main.py ./main.py
COPY --chown=appuser:appuser pytest.ini ./pytest.ini

USER appuser

EXPOSE 8000

# The health router is mounted at /health. Probe that exact path: /health/
# returns a 307 redirect, and `curl -f` treats 3xx as success — the check would
# go green while proving nothing about the app.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
