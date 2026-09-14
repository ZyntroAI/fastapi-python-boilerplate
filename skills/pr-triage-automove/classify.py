"""File classification — AST-based, not grep.

Grep cannot tell ``import auth`` inside ``app/api/auth.py`` (a sibling module)
from a real use of root ``auth.py``. Parsing can: split on ``.`` and compare the
top-level name.
"""
from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Classification:
    path: str
    bucket: str                    # keep | move | hold
    reason: str
    imported_by: list[str] = field(default_factory=list)
    referenced_by: list[str] = field(default_factory=list)
    unparseable: bool = False


def git(repo: Path, *args: str, check: bool = True) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=check
    ).stdout


def tracked_files(repo: Path) -> list[str]:
    """Tracked paths, NUL-separated so spaces and emoji survive."""
    return [f for f in git(repo, "ls-files", "-z").split("\0") if f]


def import_index(repo: Path, files: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    """module-name -> files importing it, plus the list that failed to parse.

    A file that does not parse is reported, never silently treated as having no
    importers — that is how a needed module gets archived.
    """
    index: dict[str, list[str]] = {}
    bad: list[str] = []
    for f in files:
        if not f.endswith(".py"):
            continue
        try:
            tree = ast.parse((repo / f).read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            bad.append(f)
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for n in names:
                index.setdefault(n, []).append(f)
    return index, bad


def referenced_by(
    repo: Path, name: str, files: list[str], suffixes: tuple[str, ...], self_path: str
) -> list[str]:
    """Tracked text files whose content mentions ``name`` (excluding itself)."""
    hits: list[str] = []
    for f in files:
        if f == self_path or not f.endswith(suffixes):
            continue
        p = repo / f
        if not p.is_file() or p.stat().st_size > 300_000:
            continue
        try:
            if name in p.read_text(encoding="utf-8", errors="ignore"):
                hits.append(f)
        except OSError:
            continue
    return hits


def classify(
    repo: Path, cfg: dict, stamp: str
) -> tuple[list[Classification], dict[str, list[str]]]:
    """Return (classifications, meta) for every tracked root-level file."""
    files = tracked_files(repo)
    index, unparseable = import_index(repo, files)
    canonical = set(cfg["canonical"])
    suffixes = tuple(cfg["reference_suffixes"])

    out: list[Classification] = []
    for f in sorted(x for x in files if "/" not in x):
        if f in canonical:
            out.append(Classification(f, "keep", "canonical repo file or entrypoint"))
            continue
        mod = f[:-3] if f.endswith(".py") else None
        if mod:
            users = [u for u in index.get(mod, []) if u != f]
            if users:
                out.append(Classification(f, "keep", "imported as a module", imported_by=users))
                continue
        refs = referenced_by(repo, f, files, suffixes, f)
        if refs:
            out.append(Classification(f, "hold", "still referenced by name", referenced_by=refs))
            continue
        out.append(Classification(f, "move", "unreferenced root file"))

    meta = {"unparseable_py": unparseable, "tracked_total": len(files)}
    return out, meta


def dest_for(path: str, layout: dict[str, list[str]], fallback: str) -> str:
    low = path.lower()
    for folder, exts in layout.items():
        if low.endswith(tuple(exts)):
            return folder
    return fallback
