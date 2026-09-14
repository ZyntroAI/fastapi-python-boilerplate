"""Agent Skill Template loader/validator tests."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agent_skill_template import (load_skill, resolve_layers, verify_gates,
                                  prepare_skill, SkillLoadError)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_T = os.path.join(ROOT, "templates", "agent-skill-template.v1.json")
YAML_T = os.path.join(ROOT, "templates", "agent-skill-template.v1.yaml")
EX = os.path.join(ROOT, "examples", "notebooklm-link-share.skill.yaml")


def test_load_json_template():
    s = load_skill(JSON_T)
    assert s["metadata"]["id"].startswith("skill-")


def test_load_yaml_template():
    s = load_skill(YAML_T)
    assert "loading_model" in s and "security" in s


def test_load_from_dict():
    s = load_skill({"agent_skill": {"metadata": {}, "core": {}, "loading_model": {},
                                    "execution": {}, "security": {}}})
    assert isinstance(s, dict)


def test_load_missing_agent_skill_key():
    with pytest.raises(SkillLoadError):
        load_skill({"foo": 1})


def test_load_missing_section():
    with pytest.raises(SkillLoadError):
        load_skill({"agent_skill": {"metadata": {}}})  # only metadata


def test_resolve_layers_core_always_loaded():
    s = load_skill(YAML_T)
    layers = resolve_layers(s)
    by_lvl = {l["level"]: l for l in layers}
    assert by_lvl[1]["loaded"] is True       # core
    assert by_lvl[2]["loaded"] is True       # essential
    assert by_lvl[3]["loaded"] is False      # situational skipped w/o context


def test_resolve_layers_situational_when_needed():
    s = load_skill(YAML_T)
    layers = resolve_layers(s, {"needs_situational": True})
    by_lvl = {l["level"]: l for l in layers}
    assert by_lvl[3]["loaded"] is True


def test_verify_gates_all_pass():
    s = load_skill(YAML_T)
    vg = verify_gates(s)
    assert vg["passed"] is True and vg["failed"] == []


def test_verify_gates_fails_unknown():
    s = load_skill(YAML_T)
    vg = verify_gates(s, gates=["bogus-gate"])
    assert vg["passed"] is False and "bogus-gate" in vg["failed"]


def test_prepare_skill_ready():
    res = prepare_skill(EX)
    assert res["skill"]["metadata"]["id"] == "notebooklm-link-share-v1"
    assert res["gates"]["passed"] is True
    assert len([l for l in res["layers"] if l["loaded"]]) >= 2


def test_prepare_skill_raises_on_gate_failure():
    with pytest.raises(SkillLoadError):
        prepare_skill(EX, gates=["bogus"])
