"""Permission checker — decide whether a push will be accepted BEFORE we try it.

The problem this solves
-----------------------
An automated agent pushes a branch, and the push is rejected *after* the work is
done::

    ! [remote rejected] fig/topic -> fig/topic
      (refusing to allow a GitHub App to create or update workflow
       `.github/workflows/ci.yml` without `workflows` permission)

By then the agent has burned the turn. This module answers the question up
front, from the changed path list plus the token's permission map, so the agent
can either narrow the change or hand off a patch instead.

Pure stdlib. No network, no token — you feed it what you already know.
"""

from __future__ import annotations

import re

__all__ = [
    "WORKFLOW_DIR",
    "normalize_path",
    "required_permissions",
    "check",
    "explain",
    "format_report",
]

WORKFLOW_DIR = ".github/workflows/"

# Every push needs contents: write. A push that touches .github/workflows/ also
# needs the separate `workflows` scope, which is an App-installation setting and
# NOT something a repo-level write grant can supply.
_BASE_PERMISSION = ("contents", "write")
_WORKFLOW_PERMISSION = ("workflows", "write")


def normalize_path(path: str) -> str:
    """Convert a repo-relative path to a comparable form.

    ``lstrip("./")`` is the obvious thing to reach for here and it is WRONG —
    ``str.lstrip`` takes a *set of characters*, not a prefix, so it eats the
    leading dot of ``.github/`` and the result no longer matches::

        >>> ".github/workflows/ci.yml".lstrip("./")
        'github/workflows/ci.yml'

    Strip the literal prefixes instead.
    """
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    p = p.lstrip("/")
    return p


def required_permissions(paths) -> list[list[str]]:
    """Return the permission pairs a push of ``paths`` requires."""
    required = {_BASE_PERMISSION}
    for raw in paths:
        if normalize_path(raw).startswith(WORKFLOW_DIR):
            required.add(_WORKFLOW_PERMISSION)
            break
    return [list(pair) for pair in sorted(required)]


def check(permissions: dict, paths) -> dict:
    """Decide whether a push of ``paths`` is allowed under ``permissions``.

    ``permissions`` is a GitHub App permission map, e.g.
    ``{"contents": "write", "workflows": "write"}``. Values of ``None`` and
    ``"none"`` are treated as absent.
    """
    paths = [normalize_path(p) for p in paths]
    required = required_permissions(paths)
    missing = [list(pair) for pair in required if _level(permissions, pair[0]) != "write"]

    workflow_paths = [p for p in paths if p.startswith(WORKFLOW_DIR)]
    blockers = []
    if any(pair[0] == "workflows" for pair in required) and any(
        pair[0] == "workflows" for pair in missing
    ):
        blockers.append(
            "`workflows: write` is an App-installation permission — a repo-level "
            "write grant cannot supply it. Deliver the workflow change as a patch, "
            "or ask the org owner to grant `Workflows -> Read and write`."
        )

    return {
        "can_push": not missing,
        "required": [list(pair) for pair in required],
        "missing": missing,
        "workflow_paths": workflow_paths,
        "paths": paths,
        "blockers": blockers,
    }


def explain(report: dict) -> str:
    """One-paragraph plain-language reading of a :func:`check` report."""
    if report["can_push"]:
        return (
            f"Push allowed. {len(report['paths'])} path(s) need "
            + ", ".join(f"{k}:{v}" for k, v in report["required"])
            + "."
        )
    missing = ", ".join(f"{k}:{v}" for k, v in report["missing"])
    head = f"Push will be REJECTED — missing {missing}."
    if report["workflow_paths"]:
        head += (
            " A workflow file is present in the change set, and one workflow file "
            "in a commit rejects the WHOLE push, not just that file: "
            + ", ".join(report["workflow_paths"])
            + "."
        )
    if report["blockers"]:
        head += " " + " ".join(report["blockers"])
    return head


def format_report(report: dict) -> str:
    """Markdown block suitable for pasting into a PR body or an escalation note."""
    lines = [
        "### Push permission check",
        "",
        f"- **Verdict** — {'allowed' if report['can_push'] else 'blocked'}",
        "- **Required** — " + ", ".join(f"`{k}:{v}`" for k, v in report["required"]),
    ]
    if report["missing"]:
        lines.append(
            "- **Missing** — " + ", ".join(f"`{k}:{v}`" for k, v in report["missing"])
        )
    if report["workflow_paths"]:
        lines.append(
            "- **Workflow files in change set** — "
            + ", ".join(f"`{p}`" for p in report["workflow_paths"])
        )
    for blocker in report["blockers"]:
        lines.append(f"- **Blocker** — {blocker}")
    lines.append("")
    lines.append(explain(report))
    return "\n".join(lines)


def _level(permissions: dict, key: str) -> str:
    value = (permissions or {}).get(key)
    if value is None:
        return "none"
    return str(value).lower()
