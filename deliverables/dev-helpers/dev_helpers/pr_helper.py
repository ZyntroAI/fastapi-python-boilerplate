"""PR helper — assemble a pull-request body that satisfies a Definition of Done.

Repos that require a CHANGELOG entry, a verification command, and a filled
Definition of Done tend to get PRs that assert those things in prose. This
module turns the assertions into a fixed set of fields plus a checklist derived
from what was actually done, so a missing item is visible rather than implied.

Pure stdlib.
"""

from __future__ import annotations

__all__ = ["DEFAULT_DOD", "checklist", "build_pr_body"]

DEFAULT_DOD = [
    "Steps complete or explicitly explained",
    "Acceptance criteria met and checked",
    "CHANGELOG.md updated",
    "Tests added or updated and passing",
    "No direct commits to the default branch",
]


def checklist(facts: dict | None = None, required=None) -> list[dict]:
    """Build a Definition-of-Done checklist from a facts map.

    A name present with a truthy value is checked; truthy strings are shown as
    evidence after the item. Absent or falsey names render unchecked — a visible
    gap, which is the point.
    """
    facts = facts or {}
    names = list(required) if required else DEFAULT_DOD
    rows = []
    for name in names:
        value = facts.get(name)
        rows.append(
            {
                "item": name,
                "done": bool(value),
                "evidence": value if isinstance(value, str) else None,
            }
        )
    return rows


def build_pr_body(
    summary: str,
    files,
    tests: str | None = None,
    dod_facts: dict | None = None,
    notes: str | None = None,
) -> str:
    """Render a PR body with summary, change list, verification, and DoD."""
    files = sorted({str(f).replace("\\", "/") for f in files})
    lines = ["## Summary", "", summary, "", "## Changes", ""]
    lines += [f"- `{f}`" for f in files]

    lines += ["", "## Verification", ""]
    lines.append(tests or "_Not run — state why here._")

    if dod_facts is not None:
        lines += ["", "## Definition of Done", ""]
        for row in checklist(dod_facts):
            mark = "x" if row["done"] else " "
            suffix = f" — {row['evidence']}" if row["evidence"] else ""
            lines.append(f"- [{mark}] {row['item']}{suffix}")

    if notes:
        lines += ["", "## Notes", "", notes]

    lines.append("")
    return "\n".join(lines)
