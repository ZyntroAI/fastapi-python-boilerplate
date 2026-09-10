"""BytePlusECSProvider — the only place the BytePlus SDK may be touched.

This adapter implements ComputeProvider. Everything above it is unchanged when
BytePlus is swapped out; only this file and client.py move.

The SDK calls are marked with TODO(byteplus): they are the single seam to fill
in against the real `byteplus-python-sdk`. The method signatures, the return
type, and the error behaviour are already final.
"""

from __future__ import annotations

from pure_agent.providers.base import ComputeProvider
from pure_agent.providers.byteplus.client import BytePlusClient
from pure_agent.schemas.compute import InstanceResponse


class BytePlusECSProvider(ComputeProvider):
    def __init__(self, client: BytePlusClient) -> None:
        self.client = client

    async def list_instances(self) -> list[InstanceResponse]:
        # TODO(byteplus): call ECS DescribeInstances and map the response.
        return []

    async def start_instance(self, instance_id: str) -> InstanceResponse:
        # TODO(byteplus): call ECS StartInstance.
        return InstanceResponse(instance_id=instance_id, status="starting")

    async def stop_instance(self, instance_id: str) -> InstanceResponse:
        # TODO(byteplus): call ECS StopInstance.
        return InstanceResponse(instance_id=instance_id, status="stopping")

    async def reboot_instance(self, instance_id: str) -> InstanceResponse:
        # TODO(byteplus): call ECS RebootInstance.
        return InstanceResponse(instance_id=instance_id, status="rebooting")
