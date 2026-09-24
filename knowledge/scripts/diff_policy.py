#!/usr/bin/env python3
"""CI policy gate for knowledge changes.

Validates that knowledge content is safe to index:
  1. All markdown files are valid UTF-8.
  2. Frontmatter follows standard YAML format:
     ---
     key: value
     ---
  3. No path traversal or invalid references.

Exit code: 0 = pass, 1 = block
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Auto-detect: knowledge/scripts/diff_policy.py → parents[1] = knowledge/
VAULT_DIR = Path(__file__).resolve().parents[1] / "vault"

# ✅ Fixed: raw string + correct pattern
# Matches: --- [newline] any content [newline] ---
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\s*\Z", re.DOTALL)


def check_vault(
    vault: Path,
    changed: list[str] | None = None,
) -> list[str]:
    """Validate markdown files in the vault.

    Args:
        vault: Path to vault directory
        changed: List of relative paths to check; None = check all

    Returns:
        List of error messages; empty = no issues
    """
    errors: list[str] = []

    if changed:
        # Security: prevent path traversal
        targets: list[Path] = []
        for rel_path in changed:
            if ".." in rel_path or rel_path.startswith(("/", "\\")):
                errors.append(f"path traversal attempt rejected: {rel_path}")
                continue
            full_path = (vault / rel_path).resolve()
            # Double-check within vault
            if not full_path.is_relative_to(vault):
                errors.append(f"path outside vault rejected: {rel_path}")
                continue
            targets.append(full_path)
    else:
        # Check all .md files
        targets = list(vault.rglob("*.md"))

    for file_path in targets:
        if not file_path.is_file():
            errors.append(f"missing: {file_path}")
            continue

        # Read with UTF-8 validation
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"encoding error (not UTF-8): {file_path}")
            continue

        # Validate frontmatter if present
        if text.startswith("---"):
            if not _FRONTMATTER_RE.match(text):
                errors.append(f"invalid frontmatter format: {file_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault",
        default=str(VAULT_DIR),
        help="Path to knowledge vault",
    )
    parser.add_argument(
        "--changed",
        nargs="*",
        default=[],
        help="Space-separated relative paths to validate",
    )

    args = parser.parse_args()
    vault_path = Path(args.vault).resolve()

    errors = check_vault(
        vault=vault_path,
        changed=args.changed if args.changed else None,
    )

    for err in errors:
        print(f"[policy] ❌ {err}")

    if errors:
        print(f"\n[policy] ⛔ {len(errors)} violation(s) — blocking index sync")
        return 1

    print("[policy] ✅ All checks passed — content is index-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
