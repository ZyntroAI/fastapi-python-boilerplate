"""MockComputeProvider — the reason CI needs no cloud credentials.

An in-memory provider that satisfies the same contract as the real adapter.
Unit tests run against this, so they are fast, free, and deterministic; only
integration tests touch a real sandbox account.
"""

from __future__ import annotations

from pure_agent.providers.base import ComputeProvider
from pure_agent.schemas.compute import InstanceResponse


class MockComputeProvider(ComputeProvider):
    def __init__(self, instances: list[str] | None = None) -> None:
        self._instances = list(instances or ["i-mock-001", "i-mock-002"])
        self._status: dict[str, str] = {i: "running" for i in self._instances}

    async def list_instances(self) -> list[InstanceResponse]:
        return [
            InstanceResponse(instance_id=i, status=self._status.get(i, "unknown"))
            for i in self._instances
        ]

    async def start_instance(self, instance_id: str) -> InstanceResponse:
        self._status[instance_id] = "starting"
        return InstanceResponse(instance_id=instance_id, status="starting")

    async def stop_instance(self, instance_id: str) -> InstanceResponse:
        self._status[instance_id] = "stopping"
        return InstanceResponse(instance_id=instance_id, status="stopping")

    async def reboot_instance(self, instance_id: str) -> InstanceResponse:
        self._status[instance_id] = "rebooting"
        return InstanceResponse(instance_id=instance_id, status="rebooting")
