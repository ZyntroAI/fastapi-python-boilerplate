# 🧪🔗 Full Stack + End-to-End API Test Workflow

Now tests run **through Traefik** — exactly like real users → validates your entire stack: **API → Traefik routing → PostgreSQL → Redis → back**.

---

## 📄 `.github/workflows/test-suite.yml` — Final Full Edition

```yaml
name: 🧪 Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

permissions:
  contents: read

env:
  DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/fastapi_test
  REDIS_URL: redis://redis:6379/0
  # API Base URL — through Traefik (real ingress path)
  API_BASE_URL: http://traefik:80
  COMPOSE_FILE: docker-compose.yml
  COMPOSE_PROJECT_NAME: testsuite

jobs:
  test:
    name: 🧪 Full Stack + E2E API Tests
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: 📦 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 🐳 Spin Up FULL Stack (API + DB + Redis + Traefik)
        run: |
          docker compose up -d --build
          echo "⏳ All services starting..."

      - name: ⏳ Wait for PostgreSQL
        run: |
          until docker compose exec -T postgres pg_isready -U postgres -d fastapi_test; do
            echo "Waiting for PostgreSQL..."
            sleep 3
          done
          echo "✅ PostgreSQL Ready"

      - name: ⏳ Wait for Redis
        run: |
          until docker compose exec -T redis redis-cli ping | grep PONG; do
            echo "Waiting for Redis..."
            sleep 2
          done
          echo "✅ Redis Ready"

      - name: ⏳ Wait for API (via Traefik)
        run: |
          until curl -s -o /dev/null -w "%{http_code}" ${{ env.API_BASE_URL }}/health | grep -E "200|401"; do
            echo "Waiting for API via Traefik..."
            sleep 3
          done
          echo "✅ API + Traefik Ready"

      - name: 📊 Run Database Migrations
        run: alembic upgrade head

      - name: 🧪 Run Unit & Integration Tests (direct DB access)
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=xml:coverage-unit.xml \
            -v -k "not e2e"

      - name: 🔗 Run End-to-End API Tests (through Traefik)
        run: |
          pytest tests/e2e/ \
            --cov=app \
            --cov-append \
            --cov-report=term-missing \
            --cov-report=xml:coverage.xml \
            -v -k "e2e"

      - name: 📤 Upload Combined Coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage-unit.xml,./coverage.xml
          flags: unit,e2e,full-stack
          fail_ci_if_error: false

      - name: 🧹 Cleanup Stack
        if: always()
        run: docker compose down --remove-orphans --volumes
```

---

## 📁 New Test Folder Structure

```
tests/
├── unit/              # Fast unit tests — no DB needed
│   └── tasks/
├── integration/       # Direct API/db tests — skip Traefik
├── e2e/               # ✅ NEW — End-to-end through Traefik
│   ├── test_health.py
│   ├── test_items_api.py
│   └── test_auth_flow.py
├── conftest.py
├── test_gui.py
├── test_items.py
├── test_search.py
└── test_users.py
```

---

## 📄 Example E2E Test — `tests/e2e/test_health.py`

```python
"""End-to-end tests — hit API through Traefik ingress"""
import os
import pytest
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:80")

@pytest.mark.e2e
def test_health_endpoint_through_traefik():
    """✅ Health check works via Traefik routing"""
    resp = httpx.get(f"{API_BASE}/health", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("healthy", "ok")

@pytest.mark.e2e
def test_api_swagger_ui_available():
    """✅ Swagger docs accessible via Traefik"""
    resp = httpx.get(f"{API_BASE}/docs", timeout=10)
    assert resp.status_code == 200
    assert "swagger" in resp.text.lower()
```

---

## 📄 Example E2E Test — `tests/e2e/test_items_api.py`

```python
"""End-to-end CRUD through Traefik — full stack validation"""
import os
import pytest
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:80")

@pytest.fixture
def client():
    return httpx.Client(base_url=API_BASE, timeout=15)

@pytest.mark.e2e
def test_create_and_fetch_item(client):
    """✅ Create item → verify stored → read back — through Traefik"""
    # Create
    create = client.post("/api/items", json={
        "title": "E2E Test Item",
        "description": "Created via Traefik ingress"
    })
    assert create.status_code in (200, 201)
    item = create.json()
    assert item["title"] == "E2E Test Item"
    item_id = item["id"]

    # Fetch via Traefik
    fetch = client.get(f"/api/items/{item_id}")
    assert fetch.status_code == 200
    fetched = fetch.json()
    assert fetched["id"] == item_id
    assert fetched["title"] == "E2E Test Item"

@pytest.mark.e2e
def test_list_items_through_traefik(client):
    """✅ Item list endpoint accessible through Traefik"""
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
```

---

## ✅ What This Validates Now

| Layer | What Gets Tested |
|---|---|
| 🚦 **Traefik Routing** | HTTP → correct service → correct path prefix |
| 🚀 **FastAPI App** | Endpoints, auth, validation, business logic |
| 🐘 **PostgreSQL** | Schema, constraints, queries, transactions |
| 🟥 **Redis** | Caching, sessions, rate limits, locks |
| 🔐 **Full Flow** | Request → Traefik → App → DB/Redis → Response → Verified |

---

## 📋 Required `docker-compose.yml` Additions

Ensure your API service is exposed **through Traefik** (labels enable routing):

```yaml
services:
  api:
    build: .
    depends_on: [postgres, redis]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/fastapi_test
      REDIS_URL: redis://redis:6379/0
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=PathPrefix(`/`)"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: fastapi_test
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

---

## ✅ Ready to Go!

1. **Save** the workflow → `.github/workflows/test-suite.yml`
2. **Create** the `tests/e2e/` folder with the example tests above
3. **Verify** your `docker-compose.yml` has the API + Traefik labels
4. **Push** → Every PR now tests:
   - ✅ Unit tests (fast, no DB)
   - ✅ Integration tests (direct DB access)
   - ✅ **E2E tests through Traefik** (real-world routing validation)
   - ✅ Combined coverage → Codecov → README badge

---

Would you like me to add **JWT auth flow tests** to the E2E suite — so it also validates login → get token → use protected endpoints through Traefik? 🔐✅
