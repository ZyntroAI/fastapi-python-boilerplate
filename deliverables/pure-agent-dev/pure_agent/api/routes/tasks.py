"""Task endpoint — accepts a structured AgentTask and executes it."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pure_agent.agents.executor import UnsupportedActionError
from pure_agent.api.deps import get_compute_service
from pure_agent.schemas.task import AgentTask
from pure_agent.services.compute_service import ComputeService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=None)
async def run_task(
    task: AgentTask,
    service: ComputeService = Depends(get_compute_service),
):
    try:
        return await service.execute(action=task.action, instance_id=task.instance_id)
    except UnsupportedActionError as exc:  # pragma: no cover - guarded by the model
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
