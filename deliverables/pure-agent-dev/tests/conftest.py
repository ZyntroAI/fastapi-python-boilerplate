"""Shared fixtures. Every test runs without cloud credentials."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `pure_agent` importable when pytest is run from the deliverable root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pure_agent.agents.executor import AgentExecutor  # noqa: E402
from pure_agent.agents.planner import AgentPlanner  # noqa: E402
from pure_agent.providers.mock import MockComputeProvider  # noqa: E402
from pure_agent.services.compute_service import ComputeService  # noqa: E402


@pytest.fixture
def mock_provider() -> MockComputeProvider:
    return MockComputeProvider(instances=["i-test-001", "i-test-002"])


@pytest.fixture
def planner() -> AgentPlanner:
    # Stable task ids so assertions can be exact.
    return AgentPlanner(task_id_factory=lambda: "t-fixed")


@pytest.fixture
def service(mock_provider) -> ComputeService:
    return ComputeService(
        planner=AgentPlanner(task_id_factory=lambda: "t-fixed"),
        executor=AgentExecutor(mock_provider),
    )
