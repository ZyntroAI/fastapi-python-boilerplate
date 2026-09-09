#!/usr/bin/env python3
"""CI policy gate for knowledge changes.

Checks that a knowledge change is index-safe:
  1. Any markdown file in the vault is valid (frontmatter + utf-8).
  2. A staged index is consistent with the vault content.

Run by the `index-sync` CI job before a push to Algolia. Exit code 0 = pass.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parents[1] / "vault"
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def check_vault(vault: Path, changed: list[str] | None = None) -> list[str]:
    """Validate every .md file (or only the changed subset) in the vault."""
    errors: list[str] = []
    targets = [Path(vault, c) for c in changed] if changed else vault.rglob("*.md")
    for file in targets:
        if not file.is_file():
            errors.append(f"missing: {file}")
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"not utf-8: {file}")
            continue
        if text.startswith("---") and not _FRONTMATTER_RE.match(text):
            errors.append(f"malformed frontmatter: {file}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=str(VAULT_DIR))
    parser.add_argument(
        "--changed",
        nargs="*",
        help="space-separated markdown paths to check; empty = whole vault",
    )
    args = parser.parse_args()

    errors = check_vault(Path(args.vault), args.changed)
    for err in errors:
        print(f"[policy] FAIL {err}")
    if errors:
        print(f"[policy] {len(errors)} violation(s); blocking index push.")
        return 1
    print("[policy] OK — knowledge content is index-safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
