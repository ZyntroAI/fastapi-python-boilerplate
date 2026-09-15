#!/usr/bin/env python3
"""Runnable tests for the auto-label classifier.

No network, no pytest required:

    python skills/auto-label/tests/test_classify.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classify import classify, parse_title  # noqa: E402

FAILURES = []


def check(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"     want: {sorted(want) if isinstance(want, set) else want}")
        print(f"     got:  {sorted(got) if isinstance(got, set) else got}")
        FAILURES.append(name)


# ---- title parsing ----------------------------------------------------
check("parse feat(scope)", parse_title("feat(docs): add thing")["type"], "feat")
check("parse scope", parse_title("feat(docs): add thing")["scope"], "docs")
check("parse breaking", parse_title("feat(api)!: drop v1")["breaking"], True)
check("parse noscope", parse_title("fix: patch")["scope"], "")
check("parse garbage type is empty", parse_title("just a title")["type"], "")

# ---- type rules -------------------------------------------------------
# Scope is deliberately NOT a signal: only the commit type and the changed
# paths are. `feat(docs)` with no docs/ path is a feature, not a docs change.
check("feat -> feature+enhancement (scope is not a signal)",
      classify("feat(docs): add thing", []),
      {"feature", "enhancement"})
check("feat(docs) + docs path -> docs labels from the PATH",
      classify("feat(docs): add thing", ["docs/fig/README.md"]),
      {"feature", "enhancement", "docs", "documentation"})
check("fix -> bugfix+bug",
      classify("fix: patch", []),
      {"bugfix", "bug"})
check("unparseable title gets nothing from type",
      classify("Some Random PR", []), set())

# ---- path rules -------------------------------------------------------
check("skills/** -> skills label",
      classify("chore: x", ["skills/auto-label/classify.py"]),
      {"chore", "skills 🧠", "python:uv"})
check("security/** -> security",
      classify("chore: x", ["security/cwe1321/README.md"]),
      {"chore", "security", "docs", "documentation"})
check("root-level .py matches **/*.py",
      classify("chore: x", ["main.py"]),
      {"chore", "python:uv"})
check("workflow path -> build",
      classify("chore: x", [".github/workflows/ci.yml"]),
      {"chore", "build"})
check("lockfile -> dependencies+deps",
      classify("chore: bump", ["uv.lock", "pyproject.toml"]),
      {"chore", "dependencies", "deps"})
check("tsx -> ux/ui + javascript",
      classify("chore: x", ["src/App.tsx"]),
      {"chore", "ux/ui", "javascript"})

# ---- combination + breaking ------------------------------------------
both = classify("feat(skill:x): new skill", ["skills/x/SKILL.md"])
check("feat + skills path combines", {"feature", "enhancement", "skills 🧠"} <= both, True)
check("breaking adds label",
      "breaking" in classify("feat(api)!: drop v1", []), True)

# ---- the invariants that matter --------------------------------------
check("no match -> empty set (no default label)",
      classify("Random PR title", ["some/unmapped.bin"]), set())
check("classify is deterministic",
      classify("feat(docs): a", ["docs/x.md"]),
      classify("feat(docs): a", ["docs/x.md"]))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: {FAILURES}")
    sys.exit(1)
print("ALL AUTO-LABEL TESTS PASSED")
