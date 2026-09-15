"""Import health probe — the gate that makes relocation safe.

Runs the repo's own entrypoints in a child process (so a poisoned import does not
kill the triage run) and returns a comparable signature. Two runs — before and
after a move — must produce the *same* signature. A target that was already
broken must stay broken with the same error; that is how pre-existing breakage
is told apart from damage this skill caused.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROBE = r"""
import importlib, json, os, sys
targets = json.loads(sys.argv[1])
env_keys = json.loads(sys.argv[2])
for k, v in env_keys.items():
    os.environ.setdefault(k, v)
out = []
for t in targets:
    try:
        mod = importlib.import_module(t)
        app = getattr(mod, "app", None)
        if app is None:
            out.append({"target": t, "status": "NO_APP", "signature": "-"})
        else:
            paths = sorted({getattr(r, "path", "?") for r in app.routes})
            out.append({"target": t, "status": "OK",
                        "signature": "routes=%d" % len(paths),
                        "routes": paths})
    except Exception as e:
        out.append({"target": t, "status": "FAIL",
                    "signature": "%s: %s" % (type(e).__name__, e)})
print(json.dumps(out))
"""

_PATTERNS = (
    re.compile(r"uvicorn\s+([a-zA-Z_][\w.]*):app"),
    re.compile(r"gunicorn\s+(?:[-\w]+\s+)*([a-zA-Z_][\w.]*):app"),
    re.compile(r'"module"\s*:\s*"([a-zA-Z_][\w.]*)"'),          # vercel.json
    re.compile(r'module\s*=\s*["\']([a-zA-Z_][\w.]*)["\']'),    # Procfile-ish
)

SEARCH_FILES = (
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "vercel.json",
    "Makefile", "Procfile", "app/Dockerfile", "backend/Dockerfile",
)

PROBE_FILENAME = ".pr-triage-probe.py"


def detect_targets(repo: Path, extra_roots: tuple[str, ...] = ("k8s", "helm", ".github")) -> list[str]:
    """Best-effort discovery of ASGI entrypoints from how the repo is run."""
    found: list[str] = []
    files = [repo / f for f in SEARCH_FILES]
    for root in extra_roots:
        d = repo / root
        if d.is_dir():
            files += [p for p in d.rglob("*") if p.is_file()]

    for p in files:
        if not p.is_file() or not p.name.endswith((".yml", ".yaml", ".json", ".toml", "")) \
                and p.name not in ("Dockerfile", "Makefile", "Procfile"):
            continue
        try:
            if p.stat().st_size > 200_000:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in _PATTERNS:
            for m in pat.finditer(text):
                mod = m.group(1)
                if mod not in found:
                    found.append(mod)

    # Always worth checking the obvious ones if they exist as files.
    for cand in ("main", "app.main", "app.core.main"):
        p = repo / Path(*cand.split(".")).with_suffix(".py")
        if p.is_file() and cand not in found:
            found.append(cand)
    return found


def probe(repo: Path, targets: list[str], env: dict[str, str] | None = None,
          timeout: int = 120) -> list[dict]:
    """Run the probe in a child process. Never raises — a probe that cannot run
    reports UNKNOWN, which regression() deliberately treats as harmless."""
    if not targets:
        return []
    env = env or {}
    script = repo / PROBE_FILENAME
    script.write_text(PROBE, encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), json.dumps(targets), json.dumps(env)],
            cwd=repo, capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(repo),
                 "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return [{"target": t, "status": "UNKNOWN",
                 "signature": f"probe could not run: {type(e).__name__}"}
                for t in targets]
    finally:
        script.unlink(missing_ok=True)

    if proc.returncode != 0 or not proc.stdout.strip():
        return [{"target": t, "status": "UNKNOWN",
                 "signature": f"probe could not run (rc={proc.returncode})"}
                for t in targets]
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return [{"target": t, "status": "UNKNOWN",
                 "signature": "probe output unparseable"}
                for t in targets]


def signature(rows: list[dict]) -> dict[str, str]:
    """The comparable form: target -> status:signature."""
    return {r["target"]: f"{r['status']}:{r['signature']}" for r in rows}


def regression(before: list[dict], after: list[dict]) -> list[dict]:
    """Targets that moved to a *worse* state. Empty list means safe to proceed.

    Three rules, each earned:

    * UNKNOWN is never a regression — it means the probe could not run, which is
      an environment fact, not evidence about the move.
    * A FAIL that was already a FAIL is not a regression — that is pre-existing
      breakage, and blocking on it would make the skill unusable on any repo
      that is not already green.
    * Only OK/NO_APP dropping to a lower rank counts.
    """
    b, a = signature(before), signature(after)
    rank = {"OK": 2, "NO_APP": 1, "FAIL": 0, "UNKNOWN": -1}
    out = []
    for t, after_sig in a.items():
        before_sig = b.get(t)
        if before_sig is None:
            continue
        bs = before_sig.split(":", 1)[0]
        as_ = after_sig.split(":", 1)[0]
        if as_ == "UNKNOWN":
            continue
        if rank.get(as_, 0) < rank.get(bs, 0):
            out.append({"target": t, "before": before_sig, "after": after_sig})
    return out
