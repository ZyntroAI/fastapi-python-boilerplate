Here is a complete, production-ready `backend-qa.md` file designed for your project. It consolidates quality assurance standards, automated testing guidelines, local test execution commands, and review protocols for FastAPI, SQLModel, and PostgreSQL/Alembic architectures.

---

### `backend-qa.md`

```markdown
# 🧪 Backend Quality Assurance (QA) & Testing Standards

This document establishes the testing protocols, quality assurance standards, and code verification procedures for backend services built with **FastAPI**, **SQLModel**, and **PostgreSQL**.

---

## 📌 1. Quality Assurance Standards

All backend contributions (pull requests, patches, hotfixes) must adhere to the following quality criteria:

| Area | Requirement | Verification Method |
| :--- | :--- | :--- |
| **Code Coverage** | Minimum **80%** line coverage across routers, schemas, and CRUD logic. | `pytest --cov=app` |
| **Async Isolation** | Zero blocking synchronous calls inside `async def` route handlers. | Code Review & Linter |
| **Schema Security** | Database models (`table=True`) must never be returned directly in route endpoints. | `response_model` inspection |
| **DB Migrations** | Schema modifications require a tested Alembic migration script. | `alembic upgrade head` |
| **Type Safety** | All functions, parameters, and return values must have explicit type annotations. | `mypy app` |

---

## 🛠️ 2. Test Suite Architecture

We organize tests under the `tests/` directory following standard `pytest` layout:

```text
tests/
├── conftest.py              # Shared async pytest fixtures (db session, client, auth tokens)
├── api/                     # Endpoint integration tests
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_health.py
├── unit/                    # Business logic and utility tests
│   ├── test_security.py
│   └── test_crud.py
└── database/                # Schema & migration tests
    └── test_migrations.py

```

---

## ⚡ 3. Setting Up Test Fixtures (`conftest.py`)

Always use an isolated test database session wrapped in a transaction rollback or recreated per test run.

```python
import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.core.database import get_db_session

# SQLite in-memory engine for fast local testing (or test PostgreSQL instance)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session per test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient bound to the FastAPI app with DB dependency override."""
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

```

---

## 📋 4. Test Examples

### A. Endpoint Integration Test (`tests/api/test_users.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={"email": "qa@example.com", "password": "SecurePassword123!"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "qa@example.com"
    assert "id" in data
    assert "password" not in data  # Sensitive fields must be excluded

```

### B. Async Database Query Test (`tests/unit/test_crud.py`)

```python
import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User

@pytest.mark.asyncio
async def test_user_db_insertion(db_session: AsyncSession):
    user = User(email="db_test@example.com", hashed_password="fakehash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    result = await db_session.exec(select(User).where(User.email == "db_test@example.com"))
    fetched_user = result.first()

    assert fetched_user is not None
    assert fetched_user.id == user.id

```

---

## 🏃 5. Local Test Execution Commands

Run tests locally before creating pull requests:

```bash
# Run all tests
pytest

# Run tests with detailed logs and failure stops
pytest -v -x

# Run tests with code coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/api/test_auth.py

# Run only async marked tests
pytest -m asyncio

```

---

## 🛡️ 6. Pre-Commit QA Checklist

Before requesting code review:

1. [ ] **Pass Test Suite:** All unit and integration tests pass (`pytest`).
2. [ ] **Coverage Check:** Coverage meets or exceeds target threshold (`pytest --cov=app`).
3. [ ] **Lint & Format:** Code adheres to PEP 8 standards (`ruff check .` / `black --check .`).
4. [ ] **Type Check:** No static typing errors detected (`mypy app`).
5. [ ] **Migration Check:** New DB models include corresponding Alembic migrations in `alembic/versions/`.

```

<ElicitationsGroup message="How would you like to use this file in your project?">
  <Elicitation label="Export to .github/pull_request_template.md" query="Show me how to adapt this QA checklist into a GitHub PR template (.github/pull_request_template.md)."/>
  <Elicitation label="Configure GitHub Action workflow for Pytest" query="Help me write a GitHub Actions YAML workflow that runs this Pytest suite and enforces code coverage on every PR."/>
</ElicitationsGroup>

```
