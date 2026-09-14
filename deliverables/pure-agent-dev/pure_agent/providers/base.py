"""ComputeProvider — the most important abstraction in this architecture.

Everything above this line (api, services, agents) talks to this interface and
nothing else. It does not know or care whether the implementation underneath is
BytePlus, AWS, Azure, GCP, a local Docker daemon, or a mock.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pure_agent.schemas.compute import InstanceResponse


class ComputeProvider(ABC):
    """Infrastructure abstraction. Implement one adapter per cloud."""

    @abstractmethod
    async def list_instances(self) -> list[InstanceResponse]:
        """Return every instance visible to this provider's credentials."""
        raise NotImplementedError

    @abstractmethod
    async def start_instance(self, instance_id: str) -> InstanceResponse:
        raise NotImplementedError

    @abstractmethod
    async def stop_instance(self, instance_id: str) -> InstanceResponse:
        raise NotImplementedError

    @abstractmethod
    async def reboot_instance(self, instance_id: str) -> InstanceResponse:
        raise NotImplementedError

    # -- optional lifecycle hooks -------------------------------------------
    async def aclose(self) -> None:
        """Release SDK handles. Providers overridden as needed."""
        return None
