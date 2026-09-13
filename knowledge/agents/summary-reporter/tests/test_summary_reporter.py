"""Tests for the summary-reporter skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_summary_reporter"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
SummaryReporter = _skill.SummaryReporter
TaskState = _skill.TaskState


def _tasks():
    return [
        TaskState("T-1", "Ship auth", "done"),
        TaskState("T-2", "Wire billing", "blocked", blocker="waiting on Stripe keys"),
        TaskState("T-3", "Pick database", "in_progress", needs_decision="Postgres or MySQL?"),
    ]


def test_headline_leads_with_blockers_and_decisions():
    headline = SummaryReporter().headline(_tasks())
    assert "1 item(s) blocked" in headline
    assert "1 decision(s) needed" in headline


def test_report_puts_decisions_before_status():
    report = SummaryReporter().report("Weekly update", _tasks())
    assert report.index("## Needs your decision") < report.index("## Status")


def test_blocked_section_names_the_reason():
    report = SummaryReporter().report("Weekly update", _tasks())
    assert "waiting on Stripe keys" in report


def test_counts_are_exact():
    assert SummaryReporter().counts(_tasks()) == {
        "done": 1,
        "in_progress": 1,
        "blocked": 1,
        "not_started": 0,
    }


def test_detail_is_truncated():
    tasks = [TaskState(f"T-{i}", "x", "done") for i in range(15)]
    report = SummaryReporter(max_detail_items=10).report("Big", tasks)
    assert "...and 5 more" in report


def test_empty_report_is_honest():
    assert SummaryReporter().headline([]) == "No work in flight."


def test_unknown_status_rejected():
    with pytest.raises(ValueError):
        TaskState("T-9", "x", "vibing")
