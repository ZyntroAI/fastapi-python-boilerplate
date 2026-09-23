# AI Context & Architecture Guidelines (FastAPI)

## Project Overview
- **Framework**: FastAPI (Python 3.11+)
- **Architecture**: Async RESTful API with Layered Architecture (Router -> Service -> Repository / Model)
- **Database**: PostgreSQL with SQLModel / SQLAlchemy (Async) & Alembic migrations
- **Background Tasks**: Celery / Redis / BackgroundTasks

## Tech Stack & Tooling
- **Package Manager**: `uv` or `poetry` (or `pip` with `requirements.txt`)
- **Linter & Formatter**: `ruff` (or `black` + `flake8` + `isort`)
- **Type Checker**: `mypy`
- **Testing Framework**: `pytest` + `pytest-asyncio` + `httpx`

## Key Project Commands
- **Start Dev Server**: `uvicorn app.main:app --reload`
- **Run Tests**: `pytest`
- **Run Tests with Coverage**: `pytest --cov=app --cov-report=term-missing`
- **Format & Lint Code**: `ruff format . && ruff check . --fix`
- **Database Migrations**:
  - Create migration: `alembic revision --autogenerate -m "description"`
  - Apply migrations: `alembic upgrade head`

## FastAPI & Python Best Practices
- **Asynchronous Execution**:
  - Prefer `async def` for endpoints interacting with async DB or external network calls.
  - Use standard `def` for purely CPU-bound tasks or synchronous libraries to prevent blocking the event loop.
- **Data Validation & Schemas**:
  - Explicitly define Pydantic / SQLModel models for Request Body, Query Parameters, and Response Payload (`response_model`).
  - Keep domain schemas (`schemas/`) separate from database models (`models/`).
- **Dependency Injection**:
  - Use FastAPI's `Depends()` for database sessions, authentication/authorization, and shared services.
- **Error Handling**:
  - Raise `HTTPException` with clear error detail structures.
  - Implement custom exception handlers in `app/core/exceptions.py`.

## Code Style & Formatting Rules
- **Formatting**: 4 spaces indentation, max line length of 88 characters (Black / Ruff standard).
- **Type Hints**: Strict type hinting required for all function arguments and return types.
- **Naming Conventions**:
  - `snake_case` for variables, function names, module names, and file names (e.g., `user_service.py`).
  - `PascalCase` for Classes, Pydantic models, and Exception types.
  - `UPPER_SNAKE_CASE` for constants and config keys.
- **Imports Order**:
  1. Standard library imports
  2. Third-party imports (FastAPI, Pydantic, SQLAlchemy)
  3. Local application imports (`app...`)

## Testing Rules
- Place test files under `tests/` directory matching the source layout (e.g., `tests/api/test_auth.py`).
- Use `httpx.AsyncClient` alongside FastAPI `TestClient` for endpoint integration testing.
- Ensure database fixtures use isolated test transactions or rollbacks.
