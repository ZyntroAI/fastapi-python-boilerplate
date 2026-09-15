#!/usr/bin/env python3
"""Pure label classifier for skills/auto-label.

No network, no side effects: (title, paths) -> set of labels.

The rule table lives in labels.json so behaviour can change without editing code.

    python classify.py --title "feat(docs): convert FIG_V4" --path docs/fig/README.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_PATH = HERE / "labels.json"

# Conventional Commits: type(scope)!: subject   |   type!: subject   |   type: subject
_TITLE_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)"
    r"(?:\((?P<scope>[^)]*)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<subject>.+)$"
)


def parse_title(title: str) -> dict:
    """Parse a conventional-commit title.

    Returns {"type", "scope", "breaking", "subject"}. An unparseable title
    yields type="" — the caller must treat that as 'no title signal', never
    as a guess.
    """
    m = _TITLE_RE.match((title or "").strip())
    if not m:
        return {"type": "", "scope": "", "breaking": False, "subject": title or ""}
    return {
        "type": m.group("type").lower(),
        "scope": (m.group("scope") or "").strip().lower(),
        "breaking": bool(m.group("breaking")),
        "subject": m.group("subject"),
    }


def _match_glob(path: str, pattern: str) -> bool:
    """Glob a path against a pattern, with `**/` also matching at the root.

    fnmatch is not enough: the pattern `**/*.py` does NOT match the root-level
    `main.py` in most glob implementations, but that is exactly the case this
    skill needs. The trailing-segment fallback below covers it.
    """
    import fnmatch

    if fnmatch.fnmatch(path, pattern):
        return True
    # `**/x` should also match a bare `x` at the repository root
    if pattern.startswith("**/"):
        return fnmatch.fnmatch(path, pattern[3:]) or fnmatch.fnmatch(
            path, "*" + pattern[2:]
        )
    return False


def load_rules(path: Path | str = RULES_PATH) -> list:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("rules", [])


def classify(title: str, paths, rules=None) -> set:
    """Return the set of labels for a title + changed paths.

    Flat precedence: every matching rule contributes. An empty set means the
    PR matched nothing — callers must NOT substitute a default label.
    """
    if rules is None:
        rules = load_rules()

    parsed = parse_title(title)
    ctype = parsed["type"]
    paths = list(paths or [])

    labels: set = set()

    for rule in rules:
        match = rule.get("match", {})
        hit = False

        types = match.get("type") or []
        if types and ctype and ctype in {t.lower() for t in types}:
            hit = True

        if not hit:
            for pattern in match.get("paths") or []:
                if any(_match_glob(p, pattern) for p in paths):
                    hit = True
                    break

        if hit:
            labels.update(rule.get("labels") or [])

    if parsed["breaking"]:
        labels.add("breaking")

    return labels


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Classify a PR into labels (no network).")
    ap.add_argument("--title", default="", help="PR title (conventional commit)")
    ap.add_argument("--path", action="append", default=[], help="changed path (repeatable)")
    ap.add_argument("--labels-file", default=str(RULES_PATH))
    ap.add_argument("--json", action="store_true", help="emit JSON instead of lines")
    args = ap.parse_args(argv)

    labels = classify(args.title, args.path, load_rules(args.labels_file))

    if args.json:
        print(json.dumps({"title": args.title, "paths": args.path,
                          "labels": sorted(labels)}, ensure_ascii=False, indent=2))
    else:
        if not labels:
            print("(no labels matched — this PR is left unlabelled by design)")
        for label in sorted(labels):
            print(label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
