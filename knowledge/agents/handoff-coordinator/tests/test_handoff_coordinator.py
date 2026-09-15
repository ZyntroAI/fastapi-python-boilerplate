"""Tests for the handoff-coordinator skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_handoff_coordinator"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
HandoffCoordinator = _skill.HandoffCoordinator
Handoff = _skill.Handoff


def _complete(**kw):
    base = dict(
        work_id="W-1",
        from_owner="backend",
        to_owner="frontend",
        summary="API contract finalized",
        artifacts=["openapi.json"],
        acceptance_criteria=["returns 200 on /health"],
        next_action="wire the client to /health",
    )
    base.update(kw)
    return Handoff(**base)


def test_complete_handoff_is_accepted():
    assert HandoffCoordinator().accept(_complete()) is True


def test_missing_summary_is_rejected():
    problems = HandoffCoordinator().validate(_complete(summary="   "))
    assert any("summary" in p for p in problems)


def test_missing_artifacts_is_rejected():
    problems = HandoffCoordinator().validate(_complete(artifacts=[]))
    assert any("artifacts" in p for p in problems)


def test_same_owner_is_rejected():
    problems = HandoffCoordinator().validate(_complete(to_owner="backend"))
    assert any("same" in p for p in problems)


def test_open_questions_block_only_when_required():
    h = _complete(open_questions=["which auth scheme?"])
    assert HandoffCoordinator().accept(h) is True
    assert HandoffCoordinator(require_open_questions=True).accept(h) is False


def test_receipt_points_at_next_step():
    receipt = HandoffCoordinator().receipt(_complete())
    assert receipt["status"] == "accepted"
    assert receipt["receiver_next_step"] == "wire the client to /health"


def test_batch_counts_rejections():
    out = HandoffCoordinator().batch([_complete(), _complete(work_id="W-2", summary="")])
    assert out["accepted"] == 1
    assert out["rejected_ids"] == ["W-2"]
