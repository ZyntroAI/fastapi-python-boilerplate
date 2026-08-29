---
name: fastapi-research
description: This skill should be used when the user asks to "build an API endpoint", "design a FastAPI route", "add a Pydantic schema", "implement async data processing", or write FastAPI middleware, dependencies, or research-service integrations.
when_to_use: Apply when creating or modifying FastAPI endpoints, request/response schemas, background tasks, or API-level error handling in research or data-service codebases.
argument-hint: [endpoint-or-component-name]
disable-model-invocation: false
user-invocable: true
allowed-tools: Read Edit Write Glob Grep Bash(pytest *) WebFetch
disallowed-tools: AskUserQuestion
paths:
  - "api/**/*.py"
  - "services/**/*.py"
  - "research/**/*.py"
  - "models/**/*.py"
  - "schemas/**/*.py"
effort: high
---

# FastAPI Research API Development

Expert instructions for building scalable, high-performance research APIs using FastAPI.

## Core principles

- **Type safety**: use Pydantic models for rigorous request/response validation.
- **Async first**: use `async def` for I/O-bound work to maximize throughput.
- **Dependency injection**: use FastAPI's `Depends` for modularity and testability (DB sessions, auth, config).
- **Self-documenting**: give every route a clear docstring and type hints so Swagger/OpenAPI stays accurate.

## Implementation standards

### 1. Endpoint design
- Follow REST conventions: `GET` for retrieval, `POST` for creation, `PATCH` for partial updates, `DELETE` for removal.
- Group related routes with `APIRouter`, using consistent tags and prefixes.
- Paginate every list endpoint (`limit`/`offset` or cursor-based).

### 2. Pydantic schemas
- Define separate `Create`, `Update`, and `Response` models per resource — never reuse one model across all three.
- Use `Field(...)` to document constraints and units for research parameters.
- Set `model_config = ConfigDict(from_attributes=True)` for ORM integration.

### 3. Error handling & security
- Raise `HTTPException` with precise status codes (404 missing resource, 409 conflict, 422 validation, 500 unhandled).
- Register a global exception handler so error responses share one JSON shape across the API.
- Protect research endpoints with API keys or OAuth2 scopes as appropriate; never leave internal-only routes unauthenticated.

### 4. Integration & storage
- Manage DB connections through lifespan events or dependency injection — not module-level globals.
- Use `BackgroundTasks` for long-running simulations or exports; move anything over a few seconds off the request/response cycle.

## Code style & testing

- Follow PEP 8; type-hint every function signature.
- Write tests with `TestClient` (or `httpx.AsyncClient`) and `pytest`.
- Mock external research services and databases in the test suite — no live network calls in unit tests.

## Workflow

1. Define the Pydantic schema for the request/response.
2. Implement the `async` route handler that accepts it.
3. Delegate business logic to a service/repository layer, not the route function itself.
4. Return a validated Pydantic response model.
5. Run `pytest` to confirm nothing regressed before finishing.
