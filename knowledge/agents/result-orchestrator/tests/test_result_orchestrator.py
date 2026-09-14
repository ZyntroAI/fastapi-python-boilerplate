"""Tests for the result-orchestrator skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_result_orchestrator"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
ResultOrchestrator = _skill.ResultOrchestrator
SubtaskResult = _skill.SubtaskResult
GateResult = _skill.GateResult


def test_all_pass_is_clean():
    results = [
        SubtaskResult("a", True, [GateResult("tests", True)]),
        SubtaskResult("b", True, [GateResult("lint", True)]),
    ]
    out = ResultOrchestrator().aggregate(results)
    assert out["verdict"] == "passed"
    assert out["failure_reasons"] == {}


def test_failed_gate_marks_task_failed():
    results = [SubtaskResult("a", True, [GateResult("tests", False, "3 red")])]
    out = ResultOrchestrator().aggregate(results)
    assert out["verdict"] == "failed"
    assert "quality gate failed: tests" in out["failure_reasons"]["a"]


def test_error_is_surfaced_over_gates():
    results = [SubtaskResult("a", False, error="timeout")]
    out = ResultOrchestrator().aggregate(results)
    assert out["failure_reasons"]["a"] == "timeout"


def test_threshold_allows_partial_pass():
    results = [
        SubtaskResult("a", True),
        SubtaskResult("b", False, error="boom"),
    ]
    out = ResultOrchestrator(min_pass_ratio=0.5).aggregate(results)
    assert out["verdict"] == "passed_with_warnings"
    assert out["pass_ratio"] == 0.5


def test_empty_input_is_not_a_pass():
    assert ResultOrchestrator().aggregate([])["verdict"] == "empty"


def test_blocked_by_lists_only_failures():
    results = [SubtaskResult("a", True), SubtaskResult("b", False, error="x")]
    assert ResultOrchestrator().blocked_by(results) == ["b"]


def test_bad_ratio_is_rejected():
    with pytest.raises(ValueError):
        ResultOrchestrator(min_pass_ratio=1.5)
