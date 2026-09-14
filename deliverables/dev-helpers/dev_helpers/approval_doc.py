"""Approval document generator — turn a blocked push into a request someone can grant.

When :mod:`perm_checker` says a change needs a permission the App does not have,
the useful artefact is not an error message but a request the owner can act on
in one reading: what is blocked, which files, which permission, why the narrow
grant is safe, and what happens next.

Pure stdlib.
"""

from __future__ import annotations

import datetime as _dt

__all__ = ["build_approval_doc", "render_markdown"]


def build_approval_doc(
    repo: str,
    branch: str,
    files,
    permission: str,
    reason: str,
    requested_by: str = "fig-ai-agent",
    now: _dt.datetime | None = None,
) -> dict:
    """Assemble the structured facts of an approval request.

    ``permission`` is the GitHub App permission at stake, e.g. ``"workflows"``.
    ``files`` is the change set that triggered the block.
    """
    now = now or _dt.datetime.now(_dt.timezone.utc)
    files = sorted({str(f).replace("\\", "/") for f in files})
    return {
        "repo": repo,
        "branch": branch,
        "files": files,
        "file_count": len(files),
        "permission": permission,
        "reason": reason,
        "requested_by": requested_by,
        "generated_at": now.strftime("%Y-%m-%d %H:%M UTC"),
    }


def render_markdown(doc: dict) -> str:
    """Render an approval request as markdown, ready to paste into an issue."""
    lines = [
        f"# GitHub write-access request — `{doc['permission']}`",
        "",
        f"**Repository** — `{doc['repo']}`  ",
        f"**Branch** — `{doc['branch']}`  ",
        f"**Requested by** — `{doc['requested_by']}`  ",
        f"**Generated** — {doc['generated_at']}",
        "",
        "## What is blocked",
        "",
        doc["reason"],
        "",
        "## Why this permission",
        "",
    ]

    if doc["permission"] == "workflows":
        lines += [
            "`workflows` is an **App-installation** permission. It is separate from "
            "`contents: write`, and a repository-level write grant cannot supply it — "
            "no token carries it unless the App installation was granted it "
            "explicitly. Without it, GitHub rejects a push that creates or updates "
            "**any** file under `.github/workflows/`:",
            "",
            "```",
            f"! [remote rejected] {doc['branch']}",
            "  (refusing to allow a GitHub App to create or update workflow",
            "   `.github/workflows/<file>.yml` without `workflows` permission)",
            "```",
        ]
    else:
        lines.append(
            f"`{doc['permission']}: write` is required for this change set and is not "
            "currently held by the requesting App installation."
        )

    lines += [
        "",
        "## Change set",
        "",
        f"{doc['file_count']} file(s):",
        "",
    ]
    lines += [f"- `{f}`" for f in doc["files"]]

    lines += [
        "",
        "## Why the narrow grant is safe",
        "",
        "- The change set is fully listed above and contained to this repository.",
        "- Every file is reviewable in the pull request — nothing is pushed to the "
        "default branch directly; the grant only allows preparing a branch and PR.",
        "- The grant is scoped to this repository; it does not apply organisation-wide.",
        "- If you would rather not grant it, no grant is needed: the same change can be "
        "delivered as a `.patch` file applied by a maintainer locally.",
        "",
        "## To grant",
        "",
        "1. Organisation settings → GitHub Apps → the Fig App → Configure.",
        "2. Repository access → this repository → Permissions.",
        "3. **Workflows** → **Read and write** → Save.",
        "",
        "Then re-run the blocked step; no further action is needed from the requester.",
        "",
    ]
    return "\n".join(lines)
