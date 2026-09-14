"""Orchestrator: classify → probe before → move → probe after → report.

Dry-run is the default. ``--apply`` is the only way anything moves, and even
then a regression rolls the whole move back.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _bootstrap() -> None:
    """Make this file runnable both as a script and as part of the package.

    The directory name has a hyphen, so it is not importable by name. Running
    ``python skills/pr-triage-automove/automove.py`` puts the script's own
    folder on sys.path (not the parent), so ``pr_triage_automove`` is not found
    unless we register it ourselves — which is what this does.
    """
    here = Path(__file__).resolve().parent
    if __package__ not in (None, ""):
        return
    alias = "pr_triage_automove"
    if alias not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            alias, here / "__init__.py",
            submodule_search_locations=[str(here)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)
    parent = str(here.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)


_bootstrap()

from pr_triage_automove import classify as C          # noqa: E402
from pr_triage_automove import config as CFG          # noqa: E402
from pr_triage_automove import probe as P             # noqa: E402


def _git(repo: Path, *args: str, check: bool = True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=check)


def move(repo: Path, items: list[dict]) -> tuple[list[dict], list[str]]:
    """git mv each item. Returns (moved, failures)."""
    moved, failed = [], []
    for it in items:
        src, dst = it["path"], it["dest"]
        try:
            (repo / dst).parent.mkdir(parents=True, exist_ok=True)
            _git(repo, "mv", "--", src, dst)
            moved.append(it)
        except subprocess.CalledProcessError as e:
            failed.append(f"{src}: {(e.stderr or '').strip()[:160]}")
    return moved, failed


def unstage(repo: Path, moved: list[dict]) -> None:
    """Put everything back the way it was (rollback on regression)."""
    for it in reversed(moved):
        try:
            _git(repo, "mv", "--", it["dest"], it["path"])
        except subprocess.CalledProcessError:
            pass


def render_comment(report: dict) -> str:
    counts = report["counts"]
    lines = [
        "## 🔎 PR triage — misplaced-file scan",
        "",
        f"**{counts['move']} file(s) moved** into `{report['archive_dir']}/` "
        f"· {counts['hold']} held (still referenced) · {counts['keep']} kept",
        "",
    ]

    if report["import_health"]["regressions"]:
        lines += ["> ⛔ **Import regression detected — the move was rolled back.**", ""]
        for r in report["import_health"]["regressions"]:
            lines.append(f"> - `{r['target']}`: `{r['before']}` → `{r['after']}`")
        lines.append("")
    else:
        lines += ["> ✅ Import health unchanged, verified before and after.", ""]

    if report["moved"] or report["planned"]:
        shown = report["moved"] or report.get("planned", [])
        heading = "Files moved" if report["applied"] else "Files that would move"
        lines += [f"<details><summary>{heading}</summary>", ""]
        for m in shown:
            lines.append(f"- `{m['path']}` → `{m['dest']}`")
        lines += ["", "</details>", ""]

    if report["held"]:
        lines += ["<details><summary>Held — still referenced, needs a human call</summary>", ""]
        for h in report["held"][:25]:
            refs = ", ".join(f"`{x}`" for x in h["referenced_by"][:3]) or "—"
            lines.append(f"- `{h['path']}` ← {refs}")
        lines += ["", "</details>", ""]

    lines += [
        "### Gate applied",
        "A file moves only when **all three** hold: it is not canonical, no tracked "
        "`.py` imports it as a module (AST-verified), and its name appears in no other "
        "tracked file. Nothing is deleted — `git mv` keeps history.",
        "",
        f"_Probe targets: {', '.join('`' + t + '`' for t in report['probe_targets']) or 'none found'}_",
    ]
    return "\n".join(lines)


def run(repo: Path, apply: bool = False, stamp: str | None = None,
        comment_out: Path | None = None) -> dict:
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y-%m")
    cfg = CFG.load_config(repo)
    archive_root = CFG.archive_dir(cfg, stamp)

    items, meta = C.classify(repo, cfg, stamp)
    movable = []
    for it in items:
        if it.bucket != "move":
            continue
        folder = C.dest_for(it.path, cfg["archive_layout"], CFG.ARCHIVE_FALLBACK)
        movable.append({
            "path": it.path,
            "dest": f"{archive_root}/{folder}/{it.path}",
            "reason": it.reason,
        })

    targets = cfg["probe_targets"] or P.detect_targets(repo)
    env = {"OAUTH_CLIENT_ID": "triage-probe", "JWT_SECRET": "triage-probe", "ENV": "local"}
    before = P.probe(repo, targets, env)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archive_dir": archive_root,
        "counts": {
            "move": len(movable),
            "hold": sum(1 for i in items if i.bucket == "hold"),
            "keep": sum(1 for i in items if i.bucket == "keep"),
        },
        "moved": [],
        "held": [{"path": i.path, "reason": i.reason, "referenced_by": i.referenced_by}
                 for i in items if i.bucket == "hold"],
        "kept": [{"path": i.path, "reason": i.reason} for i in items if i.bucket == "keep"],
        "planned": movable,
        "probe_targets": targets,
        "import_health": {"before": before, "after": before, "regressions": []},
        "unparseable_py": meta["unparseable_py"],
        "applied": False,
    }

    if apply and movable:
        if len(movable) > cfg["max_move"]:
            report["aborted"] = (f"refusing to move {len(movable)} files "
                                 f"(max_move={cfg['max_move']})")
            return report
        moved, failed = move(repo, movable)
        after = P.probe(repo, targets, env)
        regs = P.regression(before, after)
        report["import_health"] = {"before": before, "after": after, "regressions": regs}
        report["move_failures"] = failed

        if regs:                                  # roll back — never leave a broken tree
            unstage(repo, moved)
            report["rolled_back"] = True
        else:
            report["moved"] = moved
            report["applied"] = True

    if comment_out:
        comment_out.write_text(render_comment(report), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PR triage — misplaced-file automove")
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true", help="actually move (default: dry-run)")
    ap.add_argument("--stamp", help="YYYY-MM for the archive folder (default: now)")
    ap.add_argument("--report", type=Path, help="write the JSON report here")
    ap.add_argument("--comment", type=Path, help="write the PR comment markdown here")
    a = ap.parse_args(argv)

    rep = run(a.repo, apply=a.apply, stamp=a.stamp, comment_out=a.comment)
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.report:
        a.report.write_text(text, encoding="utf-8")
    print(text)

    if rep["import_health"]["regressions"]:
        print("REGRESSION — rolled back", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
