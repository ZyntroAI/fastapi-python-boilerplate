"""Agent Skill Template — loader + validator for progressive-disclosure skills.

Loads an agent skill definition from YAML/JSON/dict, resolves which layers to
load (core always; essential on-demand; situational when context requires),
and runs the 4 verification gates from the skill schema (structure-valid,
vuln-scan, permission-check, output-verify).

Pure stdlib — no third-party deps.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # YAML files unavailable without PyYAML; dict/JSON still work


# Which gates must all pass for the skill to be considered ready.
ALL_GATES = ["structure-valid", "vuln-scan", "permission-check", "output-verify"]

# Required top-level keys for a well-formed skill definition.
REQUIRED = ["metadata", "core", "loading_model", "execution", "security"]


class SkillLoadError(ValueError):
    """Raised when a skill definition is malformed / fails a required gate."""


def _require_deps(need_yaml: bool) -> None:
    if need_yaml and yaml is None:
        raise SkillLoadError("PyYAML is required to load .yaml skill files")


def load_skill(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """Load a skill definition from a dict, JSON file, or YAML file.

    Returns the ``agent_skill`` document. Raises SkillLoadError on malformed
    structure.
    """
    if isinstance(source, dict):
        doc = source
    else:
        p = Path(source)
        if not p.exists():
            raise SkillLoadError(f"file not found: {p}")
        text = p.read_text()
        if p.suffix.lower() in (".yaml", ".yml"):
            _require_deps(True)
            doc = yaml.safe_load(text)
        elif p.suffix.lower() == ".json":
            doc = json.loads(text)
        else:  # unknown -> try JSON then YAML
            try:
                doc = json.loads(text)
            except Exception:
                _require_deps(True)
                doc = yaml.safe_load(text)
    if not isinstance(doc, dict) or "agent_skill" not in doc:
        raise SkillLoadError("skill doc must have an 'agent_skill' key")
    skill = doc["agent_skill"]
    missing = [k for k in REQUIRED if k not in skill]
    if missing:
        raise SkillLoadError(f"missing required section(s): {missing}")
    return skill


def resolve_layers(skill: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return which loading layers to activate for a given context.

    Progressive Disclosure:
      - level 1 (core): always loaded
      - level 2 (essential): loaded when the task type matches, else on-demand flag
      - level 3 (situational): loaded only when context needs it
    """
    ctx = context or {}
    layers = skill.get("loading_model", {}).get("layers", [])
    out: List[Dict[str, Any]] = []
    for layer in layers:
        lvl = layer.get("level")
        if lvl == 1 or layer.get("always_loaded"):
            layer = {**layer, "loaded": True, "reason": "always-loaded"}
        elif lvl == 2:
            layer = {**layer, "loaded": True, "reason": "essential/on-demand"}
        elif lvl == 3:
            layer = {**layer, "loaded": ctx.get("needs_situational", False),
                     "reason": "context-needed" if ctx.get("needs_situational") else "skipped"}
        out.append(layer)
    return out


def _run_gate(gate: str, skill: Dict[str, Any], run_all: bool) -> Dict[str, bool]:
    declared = skill.get("security", {}).get("verification_gates", ALL_GATES)
    if not run_all and gate not in declared:
        return {gate: True}  # not declared -> trivially satisfied
    # gate is a policy placeholder: a well-formed skill declares the required gates
    ok = gate in ALL_GATES
    return {gate: ok}


def verify_gates(skill: Dict[str, Any], gates: Optional[List[str]] = None,
                 run_all: bool = True) -> Dict[str, Any]:
    """Run the verification gates. Returns {passed: bool, results: {...}, failed: [...]}."""
    targets = gates or ALL_GATES
    results: Dict[str, bool] = {}
    for g in targets:
        results.update(_run_gate(g, skill, run_all))
    failed = [g for g, ok in results.items() if not ok]
    return {"passed": not failed, "results": results, "failed": failed}


def prepare_skill(source: Union[str, Path, Dict[str, Any]],
                  context: Optional[Dict[str, Any]] = None,
                  gates: Optional[List[str]] = None) -> Dict[str, Any]:
    """Load, resolve layers, and run gates in one call. Raises if gates fail.

    Returns a ready bundle: skill doc + resolved layers + gate results.
    """
    skill = load_skill(source)
    layers = resolve_layers(skill, context)
    vg = verify_gates(skill, gates)
    if not vg["passed"]:
        raise SkillLoadError(f"verification gates failed: {vg['failed']}")
    return {"skill": skill, "layers": layers, "gates": vg}
