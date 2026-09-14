"""FastAPI HTTP layer."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .base import TargetClient
from .client import AgentClient
from .errors import (
    AgentAuthError,
    AgentConfigError,
    AgentError,
    AgentPollTimeoutError,
)
from .polling import poll_task
from .schemas import AgentSubmit, AgentTaskOut, AgentTaskResult, HealthOut

VERSION = "1.0.0"

router = APIRouter(prefix="/api/agent", tags=["Agent tasks"])


async def get_client() -> TargetClient:
    """Dependency: one client per request, always closed."""
    client = AgentClient()
    try:
        yield client
    finally:
        await client.aclose()


def _http_error(err: AgentError) -> HTTPException:
    if isinstance(err, AgentConfigError):
        return HTTPException(status_code=500, detail=f"configuration error: {err}")
    if isinstance(err, AgentAuthError):
        return HTTPException(status_code=502, detail="upstream rejected credentials")
    if isinstance(err, AgentPollTimeoutError):
        return HTTPException(status_code=504, detail=str(err))
    return HTTPException(status_code=502, detail=str(err))


@router.post("/submit", response_model=AgentTaskOut, summary="Submit a new task")
async def submit(
    req: AgentSubmit, client: TargetClient = Depends(get_client)
) -> AgentTaskOut:
    try:
        task_id = await client.submit({"prompt": req.prompt, **req.payload})
    except AgentError as err:
        raise _http_error(err) from err
    return AgentTaskOut(task_id=task_id, status="pending")


@router.get("/status/{task_id}", response_model=AgentTaskResult, summary="Check status")
async def status(
    task_id: str, client: TargetClient = Depends(get_client)
) -> AgentTaskResult:
    try:
        state = await client.status(task_id)
    except AgentError as err:
        raise _http_error(err) from err
    return AgentTaskResult(task_id=task_id, status=state)


@router.get(
    "/result/{task_id}",
    response_model=AgentTaskResult,
    summary="Wait for a task and return its result",
)
async def result(
    task_id: str,
    timeout: float | None = Query(default=None, gt=0),
    client: TargetClient = Depends(get_client),
) -> AgentTaskResult:
    try:
        return await poll_task(task_id, client, timeout=timeout)
    except AgentError as err:
        raise _http_error(err) from err


def create_app() -> "FastAPI":
    """App factory — keeps import side-effect free for tests."""
    from fastapi import FastAPI

    from .config import get_settings

    app = FastAPI(title="Agent Core API", version=VERSION)
    app.include_router(router)

    @app.get("/health", response_model=HealthOut, summary="Health check")
    def health() -> HealthOut:
        return HealthOut(provider=get_settings().AGENT_PROVIDER, version=VERSION)

    return app


app = create_app()
