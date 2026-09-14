"""Compute routes — the thinnest layer in the app.

A route validates input, calls the service, and returns. No business logic
lives here, and no provider is imported here.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from pure_agent.api.deps import get_compute_service
from pure_agent.schemas.compute import InstanceResponse
from pure_agent.services.compute_service import ComputeService

router = APIRouter(prefix="/compute", tags=["compute"])


async def _run(action: str, instance_id: str | None, service: ComputeService):
    return await service.execute(action=action, instance_id=instance_id)


@router.get("/instances", response_model=list[InstanceResponse])
async def list_instances(service: ComputeService = Depends(get_compute_service)):
    return await _run("list_instances", None, service)


@router.post("/instances/{instance_id}/start", response_model=InstanceResponse)
async def start_instance(
    instance_id: str, service: ComputeService = Depends(get_compute_service)
):
    return await _run("start_instance", instance_id, service)


@router.post("/instances/{instance_id}/stop", response_model=InstanceResponse)
async def stop_instance(
    instance_id: str, service: ComputeService = Depends(get_compute_service)
):
    return await _run("stop_instance", instance_id, service)


@router.post("/instances/{instance_id}/reboot", response_model=InstanceResponse)
async def reboot_instance(
    instance_id: str, service: ComputeService = Depends(get_compute_service)
):
    return await _run("reboot_instance", instance_id, service)
