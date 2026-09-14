"""Tests for the task-master skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_task_master"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
TaskMaster = _skill.TaskMaster
Subtask = _skill.Subtask
DependencyCycleError = _skill.DependencyCycleError


def _tasks():
    return [
        Subtask("design", "Design the schema", estimate_hours=3),
        Subtask("api", "Build the API", depends_on=["design"], estimate_hours=5),
        Subtask("docs", "Write the docs", depends_on=["design"], estimate_hours=2),
        Subtask("ship", "Ship it", depends_on=["api", "docs"], estimate_hours=1),
    ]


def test_waves_respect_dependencies():
    waves = TaskMaster().execution_order(_tasks())
    assert waves == [["design"], ["api", "docs"], ["ship"]]


def test_critical_path_is_longest_chain():
    assert TaskMaster().critical_path_hours(_tasks()) == 9.0


def test_cycle_is_rejected():
    cyclic = [
        Subtask("a", "A", depends_on=["b"]),
        Subtask("b", "B", depends_on=["a"]),
    ]
    with pytest.raises(DependencyCycleError):
        TaskMaster().execution_order(cyclic)


def test_unknown_dependency_is_rejected():
    with pytest.raises(ValueError):
        TaskMaster().execution_order([Subtask("a", "A", depends_on=["ghost"])])


def test_duplicate_id_is_rejected():
    with pytest.raises(ValueError):
        TaskMaster().execution_order([Subtask("a", "A"), Subtask("a", "A again")])


def test_plan_reports_parallel_width():
    plan = TaskMaster().plan("Ship the feature", _tasks())
    assert plan["wave_count"] == 3
    assert plan["parallel_width"] == 2
