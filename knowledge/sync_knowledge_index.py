#!/usr/bin/env python3
"""Build an Algolia-shaped search index from the knowledge/ notes.

Pure standard library so it runs in CI with no extra install. Emits one record
per note plus one per heading, so search hits land on a section, not a 300-line
document.

Usage:
    python knowledge/sync_knowledge_index.py --root knowledge \
        --out knowledge_index.json [--dry-run]

Exit codes: 0 = ok, 1 = validation failure (front matter missing/invalid).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
INLINE_CODE = re.compile(r"`[^`]+`")
FENCE = re.compile(r"```[\s\S]*?```")
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
EMPHASIS = re.compile(r"[*_~]{1,3}([^*_~]+)[*_~]{1,3}")
REQUIRED = ("title", "description", "tags", "doc_kind", "status", "owner", "last_reviewed")


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Return (front matter dict, body). Bare scalars and simple lists only."""
    m = FRONTMATTER.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    key = None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("- ") and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(raw.lstrip()[2:].strip().strip('"\''))
            continue
        if ":" in raw:
            key, _, val = raw.partition(":")
            key = key.strip()
            val = val.strip().strip('"\'')
            fm[key] = val if val else []
    return fm, text[m.end():]


def plain_text(md: str) -> str:
    t = FENCE.sub(" ", md)
    t = INLINE_CODE.sub(" ", t)
    t = MD_LINK.sub(r"\1", t)
    t = HEADING.sub(r"\2", t)
    t = EMPHASIS.sub(r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def sections(body: str) -> list[tuple[str, str]]:
    """Split body into (heading, text) pairs; leading text uses the note title."""
    marks = list(HEADING.finditer(body))
    out: list[tuple[str, str]] = []
    if not marks:
        return [("", body)]
    if marks[0].start() > 0:
        out.append(("", body[: marks[0].start()]))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out.append((m.group(2).strip(), body[m.start():end]))
    return out


def build(root: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in {"README.md"}:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"not utf-8: {rel}")
            continue
        fm, body = parse_front_matter(text)
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"{rel}: missing front matter keys {missing}")
            continue
        base = {
            "note": rel,
            "title": fm["title"],
            "description": fm["description"],
            "tags": fm.get("tags", []),
            "doc_kind": fm.get("doc_kind", ""),
            "area": fm.get("supabase_area", ""),
            "body_hash": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
        }
        for i, (head, chunk) in enumerate(sections(body)):
            records.append({
                **base,
                "objectID": rel if not head else f"{rel}#{head}",
                "section": head or fm["title"],
                "content": plain_text(chunk)[:5000],
            })
    return records, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="knowledge")
    ap.add_argument("--out", default="knowledge_index.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"[index] ERROR root not found: {root}", file=sys.stderr)
        return 1

    records, errors = build(root)
    for err in errors:
        print(f"[index] FAIL {err}", file=sys.stderr)
    if errors:
        print(f"[index] {len(errors)} note(s) failed validation; refusing to index.",
              file=sys.stderr)
        return 1

    notes = {r["note"] for r in records}
    print(f"[index] {len(notes)} note(s), {len(records)} record(s)")
    payload = {"source": "knowledge", "note_count": len(notes),
               "record_count": len(records), "records": records}
    if args.dry_run:
        for r in records[:8]:
            print(f"  - {r['objectID']}")
        print("[index] dry-run: nothing written")
        return 0

    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"[index] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
