"""Planner: intent -> structured AgentTask. It must not touch a provider."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pure_agent.agents.planner import AgentPlanner
from pure_agent.schemas.task import AgentTask


def test_plan_builds_a_task(planner):
    task = planner.plan("list_instances")
    assert isinstance(task, AgentTask)
    assert task.task_id == "t-fixed"
    assert task.action == "list_instances"
    assert task.instance_id is None


def test_plan_carries_instance_id(planner):
    task = planner.plan("start_instance", "i-42")
    assert task.instance_id == "i-42"


def test_every_allowed_action_plans():
    planner = AgentPlanner(task_id_factory=lambda: "t")
    for action in ("list_instances", "start_instance", "stop_instance", "reboot_instance"):
        iid = None if action == "list_instances" else "i-1"
        assert planner.plan(action, iid).action == action


def test_unknown_action_is_rejected(planner):
    with pytest.raises(ValidationError):
        planner.plan("delete_everything")


@pytest.mark.parametrize("action", ["start_instance", "stop_instance", "reboot_instance"])
def test_instance_actions_require_instance_id(planner, action):
    with pytest.raises(ValidationError):
        planner.plan(action)


def test_task_id_is_generated_by_default():
    task = AgentPlanner().plan("list_instances")
    assert task.task_id  # non-empty uuid


def test_planner_module_has_no_provider_imports():
    """The strongest form of the rule: the Planner cannot reach a provider at all."""
    import inspect

    from pure_agent.agents import planner as planner_module

    source = inspect.getsource(planner_module)
    assert "byteplus" not in source.lower()
    assert "providers" not in source
