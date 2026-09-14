"""Tests for the blocker-resolver skill."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load():
    """Load the skill's main.py by path -- kebab-case dirs are not packages."""
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    mod_name = "agent_skill_blocker_resolver"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, main_py)
    assert spec and spec.loader, f"cannot load {main_py}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_skill = _load()
BlockerResolver = _skill.BlockerResolver
Blocker = _skill.Blocker


def test_dependency_is_self_resolvable():
    res = BlockerResolver().resolve(Blocker("b1", "missing lib", "dependency"))
    assert res.escalate is False
    assert "pin the missing dependency" in res.action


def test_permission_always_escalates():
    res = BlockerResolver().resolve(
        Blocker("b2", "no workflows scope", "permission", waiting_on="repo admin")
    )
    assert res.escalate is True
    assert res.escalate_to == "repo admin"
    assert res.owner_blocked is True


def test_exhausted_attempts_escalate():
    res = BlockerResolver(max_self_attempts=2).resolve(
        Blocker("b3", "flaky env", "environment", attempts=2)
    )
    assert res.escalate is True


def test_triage_splits_the_set():
    blockers = [
        Blocker("b1", "missing lib", "dependency"),
        Blocker("b2", "no scope", "permission"),
        Blocker("b3", "bad data", "data"),
    ]
    out = BlockerResolver().triage(blockers)
    assert out["self_resolvable"] == 2
    assert out["needs_escalation"] == 1
    assert out["escalation_ids"] == ["b2"]


def test_unknown_category_is_rejected():
    with pytest.raises(ValueError):
        BlockerResolver().resolve(Blocker("b4", "weird", "cosmic_rays"))


def test_empty_triage():
    out = BlockerResolver().triage([])
    assert out["total"] == 0
    assert out["needs_escalation"] == 0
