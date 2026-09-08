# Agent Skill Template — Progressive-Disclosure Loader + Validator

Standard, machine-readable template for defining agent skills (JSON + YAML),
with a pure-stdlib loader that implements the skill's own structure:
3-level **Progressive Disclosure** loading + 4 **verification gates**.

## Contents
- `templates/agent-skill-template.v1.yaml` / `.json` — canonical empty template.
- `examples/notebooklm-link-share.skill.yaml` — filled example (matches the
  `deliverables/notebooklm-link-share` skill).
- `agent_skill_template/` — loader/validator package.
- `tests/` — 11 tests.

## Usage
```python
from agent_skill_template import load_skill, prepare_skill

# Load (dict / .json / .yaml)
skill = load_skill("examples/notebooklm-link-share.skill.yaml")

# Resolve progressive layers for a context + run the 4 gates
bundle = prepare_skill("examples/notebooklm-link-share.skill.yaml",
                       context={"needs_situational": True})
print(bundle["layers"])   # which levels loaded
print(bundle["gates"])    # structure-valid / vuln-scan / permission-check / output-verify
```

## Progressive Disclosure
- Level 1 (core) — always loaded.
- Level 2 (essential) — on-demand / task-matched.
- Level 3 (situational) — loaded only when the context needs it (saves tokens).

## Test
```bash
python -m pytest tests/ -q    # 11 passed
```
