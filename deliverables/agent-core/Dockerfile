# Base image pinned by digest for reproducible builds.
FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first so the layer caches across source-only changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application source only — tests, charts and docs stay out of the image.
COPY agent_core/ ./agent_core/

# Non-root. UID 10001 is outside the reserved system range.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser
USER 10001

EXPOSE 8000

# No curl in slim — probe with the interpreter that is already there.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "agent_core.api:app", "--host", "0.0.0.0", "--port", "8000"]
