"""Workflow-file safety: YAML validation and action pin resolution.

Two rules, both learned the hard way on this repo:

1. A string containing a colon must be quoted. ``- name: build: prod`` parses;
   ``- name: :x:`` does not — a YAML ``ScannerError``.
2. Every ``uses:`` action reference must be a full 40-character commit SHA. A
   tag is mutable and a SHA is not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<ref>[^\s#]+)", re.MULTILINE)


@dataclass
class YamlCheck:
    path: str
    valid: bool
    error: str = ""
    mark: dict[str, int] = field(default_factory=dict)
    problem: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "valid": self.valid,
            "error": self.error,
            "mark": self.mark,
            "problem": self.problem,
        }


def validate_yaml_file(path: str | Path) -> YamlCheck:
    """Parse a YAML file and, on failure, name the exact line and column."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        return YamlCheck(str(p), False, str(exc))
    try:
        yaml.safe_load(text)
        return YamlCheck(str(p), True)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = (mark.line + 1) if mark else 0
        col = (mark.column + 1) if mark else 0
        problem = getattr(exc, "problem", str(exc)) or str(exc)
        rendered = text.splitlines()
        offending = rendered[line - 1] if 0 < line <= len(rendered) else ""
        hint = ""
        if offending.strip() and ":" in offending and not _colon_is_quoted(offending):
            hint = (
                f" Unquoted colon in value: {offending.strip()!r} — quote the string "
                '(e.g. `:x:` → `":x:"`) so the scanner does not read a mapping.'
            )
        return YamlCheck(
            str(p),
            False,
            f"line {line}, column {col}: {problem}",
            {"line": line, "column": col},
            f"{problem}{hint}",
        )


def _colon_is_quoted(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith("-"):
        stripped = stripped[1:].strip()
    _, _, value = stripped.partition(":")
    value = value.strip()
    if not value:
        return True
    return value[0] in ("'", '"', "[", "{", "|", ">", "*", "&") or value.startswith("!!")


@dataclass
class ActionRef:
    file: str
    line: int
    raw: str
    action: str
    ref: str
    pinned: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "line": self.line,
            "raw": self.raw,
            "action": self.action,
            "ref": self.ref,
            "pinned": self.pinned,
        }


def find_action_refs(path: str | Path) -> list[ActionRef]:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    refs: list[ActionRef] = []
    for i, line in enumerate(text.splitlines(), start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        raw = match.group("ref").strip().strip('"').strip("'")
        if raw.startswith("./") or raw.startswith("docker://"):
            continue  # local composite action or docker image — no SHA to pin
        action, _, ref = raw.rpartition("@")
        if not action:
            continue
        refs.append(ActionRef(str(p), i, raw, action, ref, bool(SHA_RE.match(ref))))
    return refs


def is_sha_pinned(ref: str) -> bool:
    return bool(SHA_RE.match(ref))


@dataclass
class PinAudit:
    files_scanned: int
    total_refs: int
    pinned: int
    unpinned: list[ActionRef]

    @property
    def compliant(self) -> bool:
        return not self.unpinned

    def as_dict(self) -> dict[str, object]:
        return {
            "files_scanned": self.files_scanned,
            "total_refs": self.total_refs,
            "pinned": self.pinned,
            "unpinned_count": len(self.unpinned),
            "unpinned": [r.as_dict() for r in self.unpinned],
            "compliant": self.compliant,
        }


def audit_pins(root: str | Path, patterns: tuple[str, ...] = ("*.yml", "*.yaml")) -> PinAudit:
    base = Path(root)
    files = 0
    refs: list[ActionRef] = []
    for pattern in patterns:
        for path in sorted(base.rglob(pattern)):
            if ".git" in path.parts:
                continue
            found = find_action_refs(path)
            files += 1
            refs.extend(found)
    unpinned = [r for r in refs if not r.pinned]
    return PinAudit(files, len(refs), len(refs) - len(unpinned), unpinned)


def resolve_sha(action: str, ref: str, timeout: float = 15.0) -> str | None:
    """Resolve a tag or branch to its commit SHA via the GitHub API.

    Network-dependent by design: returns ``None`` rather than guessing, so the
    caller reports an unresolved pin instead of writing in a wrong one.
    """
    try:
        import httpx
    except ImportError:  # pragma: no cover - httpx is optional at runtime
        return None
    try:
        resp = httpx.get(
            f"https://api.github.com/repos/{action}/commits/{ref}",
            headers={"Accept": "application/vnd.github+json"},
            timeout=timeout,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        sha = resp.json().get("sha", "")
        return sha if SHA_RE.match(sha) else None
    except Exception:
        return None
