"""Dependency wiring.

Provider selection is resolved here, once, and injected. Routes never import a
concrete provider, so changing COMPUTE_PROVIDER is a config change, not a code
change.
"""

from __future__ import annotations

from fastapi import Depends

from pure_agent.agents.executor import AgentExecutor
from pure_agent.agents.planner import AgentPlanner
from pure_agent.config import ProviderName, selected_provider
from pure_agent.providers.base import ComputeProvider
from pure_agent.providers.mock import MockComputeProvider
from pure_agent.services.compute_service import ComputeService


def get_provider() -> ComputeProvider:
    if selected_provider() is ProviderName.BYTEPLUS:
        # Imported lazily so that mock-only deployments never need SDK credentials.
        from pure_agent.providers.byteplus.client import BytePlusClient
        from pure_agent.providers.byteplus.ecs import BytePlusECSProvider

        return BytePlusECSProvider(BytePlusClient.from_env())
    return MockComputeProvider()


def get_compute_service(
    provider: ComputeProvider = Depends(get_provider),
) -> ComputeService:
    return ComputeService(planner=AgentPlanner(), executor=AgentExecutor(provider))
