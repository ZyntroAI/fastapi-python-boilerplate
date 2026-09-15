"""Tests for the milestone-tracker skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_milestone_tracker"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
MilestoneTracker = _skill.MilestoneTracker
Milestone = _skill.Milestone


def test_complete_beats_slip():
    m = Milestone("a", "Phase A", planned_days=10, actual_days=20, complete=True)
    assert MilestoneTracker().grade(m) == "complete"


def test_on_track_inside_threshold():
    m = Milestone("a", "Phase A", planned_days=10, actual_days=11)
    assert MilestoneTracker().grade(m) == "on_track"


def test_at_risk_and_delayed_thresholds():
    tracker = MilestoneTracker()
    assert tracker.grade(Milestone("a", "A", 10, 12)) == "at_risk"
    assert tracker.grade(Milestone("b", "B", 10, 15)) == "delayed"


def test_health_rollup_flags_delay():
    ms = [
        Milestone("a", "A", 10, 10, complete=True),
        Milestone("b", "B", 10, 15),
    ]
    out = MilestoneTracker().health(ms)
    assert out["overall"] == "delayed"
    assert out["percent_complete"] == 50.0
    assert out["total_slip_days"] == 5.0


def test_at_risk_ids_sorted_by_slip():
    ms = [Milestone("a", "A", 10, 12), Milestone("b", "B", 10, 16)]
    assert MilestoneTracker().at_risk_ids(ms) == ["b", "a"]


def test_empty_is_explicit():
    assert MilestoneTracker().health([])["overall"] == "empty"


def test_bad_thresholds_rejected():
    with pytest.raises(ValueError):
        MilestoneTracker(at_risk_slip_ratio=0.5, delayed_slip_ratio=0.2)
