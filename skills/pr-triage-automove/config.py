"""Config for pr-triage-automove.

Config-driven on purpose: the canonical allow-list and the roots to scan are
data, so a different repo adopts the skill by editing a JSON file rather than
the code.
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CANONICAL = [
    # repo meta
    "README.md", "LICENSE", "LICENSE.md", "SECURITY.md", "CONTRIBUTING.md",
    "CHANGELOG.md", "ROADMAP.md", "TASKS.md", "PROBLEMS.md", "RELEASE.md",
    "CODE_OF_CONDUCT.md", "FILE-MANIFEST.md",
    # python
    "requirements.txt", "requirements-dev.txt", "pytest.ini", "tox.ini",
    "setup.py", "setup.cfg", "pyproject.toml", ".python-version",
    # node / frontend
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "tsconfig.json", "vercel.json", "vitest.config.mjs", "next.config.js",
    # containers / build
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Makefile",
    # dotfiles
    ".gitignore", ".dockerignore", ".npmignore", ".editorconfig",
    ".env", ".env.example", ".coderabbit.yaml",
    # python entrypoints — must stay importable
    "main.py", "app.py", "asgi.py", "wsgi.py", "manage.py",
]

DEFAULT_SCAN_ROOTS = ["."]

# Dependency surface used by the reference scan — a file named in any of these
# is parked. Text formats only; binaries are skipped by size.
REFERENCE_SUFFIXES = (
    ".md", ".yml", ".yaml", ".json", ".toml", ".txt", ".sh", ".mjs", ".js",
    ".cfg", ".ini", ".service", "Makefile", "Dockerfile",
)

ARCHIVE_FALLBACK = "misc"

ARCHIVE_LAYOUT = {
    "scripts": (".py",),
    "manifests": (".yml", ".yaml", ".json"),
    "exports": (".csv", ".txt", ".patch", ".log"),
    "html": (".html", ".htm"),
    "assets": (".png", ".jpg", ".jpeg", ".svg", ".woff2", ".woff", ".ttf", ".zip"),
    "notes": (".md",),
}
ARCHIVE_FALLBACK = "misc"


def load_config(repo: Path) -> dict:
    """Merge an optional ``.pr-triage-automove.json`` over the defaults."""
    cfg = {
        "canonical": list(DEFAULT_CANONICAL),
        "scan_roots": list(DEFAULT_SCAN_ROOTS),
        "archive_dir": None,          # None -> archive/root-<YYYY-MM>
        "probe_targets": [],          # [] -> auto-detect entrypoints
        "max_move": 500,              # refuse to move more than this in one run
        "reference_suffixes": list(REFERENCE_SUFFIXES),
        "archive_layout": {k: list(v) for k, v in ARCHIVE_LAYOUT.items()},
    }
    overlay = repo / ".pr-triage-automove.json"
    if overlay.is_file():
        try:
            user = json.loads(overlay.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            user = {}
        for k, v in user.items():
            if k in cfg and isinstance(v, dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    return cfg


def archive_dir(cfg: dict, stamp: str) -> str:
    return cfg.get("archive_dir") or f"archive/root-{stamp}"
