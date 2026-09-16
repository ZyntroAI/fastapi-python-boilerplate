"""CI workflow inspector — SHA-pin audit and YAML parse state.

Two failures account for most "our CI is flaky / our CI is dead" reports:

1. **Unpinned actions.** ``uses: actions/checkout@v4`` resolves to whatever that
   tag points at today. A compromised or retagged upstream changes what runs in
   your build with no diff in your repo. A pinned ref is a 40-hex commit SHA.
2. **Files that do not parse.** A YAML error means the workflow silently never
   runs — GitHub shows no failure on the PR, so the gate looks green because it
   is absent, not because it passed.

Pure stdlib. YAML parsing is attempted with PyYAML when present and degrades to
a structural check when it is not, so the tool runs in any environment.
"""

from __future__ import annotations

import os
import re

__all__ = [
    "SHA_RE",
    "USES_RE",
    "is_pinned",
    "iter_uses",
    "scan_pins",
    "parse_state",
    "scan_workflows",
]

# 40-hex commit SHA, optionally followed by a `# v1.2.3` comment.
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+)\s*(?:#\s*(.*))?$")
_SHA_COMMENT_RE = re.compile(r"^([0-9a-f]{40})(?:\s+#.*)?$", re.IGNORECASE)


def is_pinned(ref: str) -> bool:
    """True when ``ref`` is a full commit SHA (optionally with a version comment)."""
    ref = ref.strip()
    if SHA_RE.match(ref):
        return True
    return bool(_SHA_COMMENT_RE.match(ref))


def iter_uses(text: str):
    """Yield ``(line_number, ref)`` for every ``uses:`` line, excluding locals."""
    for number, line in enumerate(text.splitlines(), start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        ref = match.group(1).strip().strip("'\"")
        if ref.startswith("./") or ref.startswith("docker://"):
            continue
        yield number, ref


def scan_pins(text: str) -> dict:
    """Return the pinned/unpinned split for one workflow body."""
    pinned, unpinned = [], []
    for number, ref in iter_uses(text):
        entry = {"line": number, "ref": ref, "action": ref.split("@", 1)[0]}
        (pinned if is_pinned(ref.split("@", 1)[-1]) else unpinned).append(entry)
    return {
        "total": len(pinned) + len(unpinned),
        "pinned": pinned,
        "unpinned": unpinned,
    }


def parse_state(text: str) -> dict:
    """Report whether a workflow body parses as YAML.

    Uses PyYAML when installed; otherwise falls back to a conservative
    indentation/colon check and says so in ``engine``.
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        return {"parses": _structural_ok(text), "engine": "structural", "error": None}

    try:
        yaml.safe_load(text)
        return {"parses": True, "engine": "pyyaml", "error": None}
    except Exception as exc:  # pragma: no cover - depends on the bad input
        return {"parses": False, "engine": "pyyaml", "error": str(exc)}


def scan_workflows(root: str = ".") -> dict:
    """Walk ``<root>/.github/workflows`` and audit every file."""
    directory = os.path.join(root, ".github", "workflows")
    files = []
    if os.path.isdir(directory):
        names = sorted(n for n in os.listdir(directory) if os.path.isfile(os.path.join(directory, n)))
    else:
        names = []

    unpinned_total = 0
    broken = []
    for name in names:
        with open(os.path.join(directory, name), "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        pins = scan_pins(text)
        state = parse_state(text)
        unpinned_total += len(pins["unpinned"])
        if not state["parses"]:
            broken.append({"file": name, "error": state["error"]})
        files.append(
            {
                "file": name,
                "total_uses": pins["total"],
                "unpinned": pins["unpinned"],
                "parses": state["parses"],
                "engine": state["engine"],
            }
        )

    return {
        "dir": directory,
        "files": files,
        "count": len(files),
        "unpinned_total": unpinned_total,
        "unparseable": broken,
    }


def _structural_ok(text: str) -> bool:
    """Conservative fallback: tabs and lines with no colon are YAML hazards."""
    if "\t" in text:
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") or ":" in stripped:
            continue
        return False
    return True
