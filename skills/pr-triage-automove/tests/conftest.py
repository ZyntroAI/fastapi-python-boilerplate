"""Load the skill package from its hyphenated directory.

``skills/pr-triage-automove/`` is not a valid Python identifier, so it cannot be
imported by name. Registering an alias package with explicit search locations
gives both ``from pr_triage_automove import x`` (tests) and the internal
``from . import probe`` (automove.py) the same module objects — which is what
lets tests monkeypatch ``probe.probe`` and have it take effect.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]      # skills/pr-triage-automove
ALIAS = "pr_triage_automove"


def _register() -> None:
    if ALIAS in sys.modules:
        return
    spec = importlib.util.spec_from_file_location(
        ALIAS,
        SKILL_DIR / "__init__.py",
        submodule_search_locations=[str(SKILL_DIR)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[ALIAS] = module
    spec.loader.exec_module(module)


_register()
