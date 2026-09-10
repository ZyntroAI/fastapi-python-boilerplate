"""Service: orchestration only — plan, then execute."""

from __future__ import annotations


async def test_service_orchestrates_planner_and_executor(service):
    result = await service.execute("start_instance", "i-test-001")
    assert result.instance_id == "i-test-001"
    assert result.status == "starting"


async def test_service_lists_instances(service):
    result = await service.execute("list_instances")
    assert len(result) == 2


async def test_service_passes_instance_id_through(service):
    """A regression here would send the wrong id to the provider."""
    result = await service.execute("stop_instance", "i-test-002")
    assert result.instance_id == "i-test-002"


async def test_service_plans_before_executing(mock_provider):
    """If the plan step were skipped, the executor would never be reached."""
    from pure_agent.agents.executor import AgentExecutor
    from pure_agent.agents.planner import AgentPlanner
    from pure_agent.services.compute_service import ComputeService

    seen = []

    class SpyPlanner(AgentPlanner):
        def plan(self, action, instance_id=None):
            seen.append(action)
            return super().plan(action, instance_id)

    svc = ComputeService(SpyPlanner(), AgentExecutor(mock_provider))
    await svc.execute("list_instances")
    assert seen == ["list_instances"]
