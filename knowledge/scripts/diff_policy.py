#!/usr/bin/env python3
"""CI policy gate for knowledge changes.

Checks that a knowledge change is index-safe:
  1. Every note in the vault is valid (utf-8 + YAML front matter with all
     required keys), matching the rules in `sync_knowledge_index.py`.
  2. A staged index (if given) is consistent with the vault content and is not
     stale with respect to the note bodies.

Run by the `index-sync` CI job before a push to Algolia. Exit code 0 = pass.

The vault is this script's parent directory — i.e. `knowledge/`. There is no
`knowledge/vault/` subfolder; the notes live directly in `knowledge/`.

Usage:
    python knowledge/scripts/diff_policy.py
    python knowledge/scripts/diff_policy.py --changed note-a.md note-b.md
    python knowledge/scripts/diff_policy.py --index knowledge_index.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# knowledge/scripts/diff_policy.py -> parents[0]=scripts, parents[1]=knowledge
VAULT_DIR = Path(__file__).resolve().parents[1]

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
_FENCE_RE = re.compile(r"```[\s\S]*?```")

# Kept in lockstep with sync_knowledge_index.py:REQUIRED.
REQUIRED = ("title", "description", "tags", "doc_kind", "status", "owner", "last_reviewed")

# Files that are structure, not content: they carry no front matter by design.
SKIP_NAMES = {"README.md"}


def body_of(text: str) -> str:
    """The note body with YAML front matter stripped — the same slice the indexer hashes."""
    match = _FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


def body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def parse_front_matter(text: str) -> dict:
    """Parse bare `key: value` scalars and `- item` lists, ignoring indentation."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm: dict = {}
    key = None
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("- ") and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(raw.lstrip()[2:].strip().strip("\"'"))
            continue
        if ":" in raw:
            key, _, val = raw.partition(":")
            key = key.strip()
            val = val.strip().strip("\"'")
            fm[key] = val if val else []
    return fm


def check_vault(vault: Path, changed: list[str] | None = None) -> tuple[list[str], int]:
    """Validate notes (or only the changed subset). Returns (errors, notes_checked)."""
    errors: list[str] = []

    if not vault.is_dir():
        return [f"vault directory not found: {vault}"], 0

    if changed:
        targets = []
        for c in changed:
            if not c.endswith(".md"):
                continue  # only notes are policed; scripts/config are not content
            p = Path(c)
            targets.append(p if p.is_absolute() else vault / p)
    else:
        targets = sorted(vault.rglob("*.md"))

    checked = 0
    for file in targets:
        if file.name in SKIP_NAMES:
            continue
        if not file.is_file():
            errors.append(f"missing: {file}")
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"not utf-8: {file}")
            continue

        checked += 1
        if not _FRONTMATTER_RE.match(text):
            errors.append(f"missing front matter: {file}")
            continue

        fm = parse_front_matter(text)
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"missing front matter keys {missing}: {file}")
        if not body_of(text).strip():
            errors.append(f"empty body: {file}")
    return errors, checked


def check_index(index: Path, vault: Path) -> list[str]:
    """A staged index must cover every note and carry current body hashes."""
    errors: list[str] = []
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"index unreadable: {index} ({exc})"]

    records = data.get("records")
    if not isinstance(records, list):
        return [f"index has no 'records' list: {index}"]

    # note path -> body hash of the note on disk
    on_disk = {
        p.relative_to(vault).as_posix(): body_hash(body_of(p.read_text(encoding="utf-8")))
        for p in sorted(vault.rglob("*.md"))
        if p.name not in SKIP_NAMES
    }

    if data.get("note_count") not in (None, len(on_disk)):
        errors.append(
            f"index note_count={data.get('note_count')} but vault has {len(on_disk)} note(s)"
        )

    indexed = {r.get("note") for r in records if isinstance(r, dict)}
    for note in on_disk:
        if note not in indexed:
            errors.append(f"note not in index: {note}")

    seen: set[str] = set()
    for rec in records:
        if not isinstance(rec, dict):
            errors.append("index record is not an object")
            continue
        note = rec.get("note")
        if note in seen or note not in on_disk:
            continue
        seen.add(note)
        if rec.get("body_hash") != on_disk[note]:
            errors.append(f"stale body_hash in index: {note}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=str(VAULT_DIR),
                        help="knowledge directory (default: this script's parent)")
    parser.add_argument("--changed", nargs="*",
                        help="markdown paths to check; empty = whole vault")
    parser.add_argument("--index", default=None,
                        help="staged index JSON to check for staleness")
    args = parser.parse_args()

    vault = Path(args.vault)
    errors, checked = check_vault(vault, args.changed)
    if args.index:
        errors += check_index(Path(args.index), vault)

    for err in errors:
        print(f"[policy] FAIL {err}")
    if errors:
        print(f"[policy] {len(errors)} violation(s); blocking index push.")
        return 1
    print(f"[policy] OK — {checked} note(s) index-safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
