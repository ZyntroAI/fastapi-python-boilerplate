#!/usr/bin/env python3
"""Regenerate knowledge/README.md from the notes themselves.

Hand-editing the index is how counts drift: the tag table carries a per-tag note
count and a member list, and adding one note can change several rows. Deriving
every number from the files keeps the README and the notes in step.

Usage:  python3 knowledge/build_knowledge_readme.py [--check]
        --check  exit 1 if the README on disk differs (for CI)
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("knowledge")
README = ROOT / "README.md"
DATE_RE = re.compile(r"^\*\*Last updated:\*\* (.+)$", re.M)


def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: no front matter")
    fm: dict = {"tags": []}
    for raw in m.group(1).splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("- "):
            fm["tags"].append(raw.lstrip()[2:].strip().strip("\"'"))
            continue
        k, _, v = raw.partition(":")
        k = k.strip()
        v = v.strip().strip("\"'")
        if not v:
            # `tags:` with no inline value introduces a block list; seed the list
            # rather than storing an empty string, or the `- item` lines that
            # follow have nothing to append to.
            fm.setdefault(k, [])
            continue
        fm[k] = v
    fm["_body"] = text[m.end():]
    fm["_path"] = path
    return fm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    notes = [parse(p) for p in sorted(ROOT.glob("*.md")) if p.name != "README.md"]

    # keep the existing review date if the file has one, else default to newest note
    current = README.read_text(encoding="utf-8")
    dm = DATE_RE.search(current)
    if dm:
        last_updated = dm.group(1).strip()
    else:
        last_updated = max(n.get("last_reviewed", "") for n in notes)

    rows = []
    for n in notes:
        words = len(re.findall(r"\S+", n["_body"]))
        # sources = numbered entries in this note's own citation block
        src = len(re.findall(r"^\[\d+\]", n["_body"], re.M))
        rows.append((n["title"], n["_path"].name, n.get("supabase_area", ""), src, words))

    tags: dict[str, list[str]] = defaultdict(list)
    for n in notes:
        for t in n["tags"]:
            tags[t].append(n["_path"].name)

    out = [
        "# Knowledge Base",
        "",
        "Curated, source-referenced notes that support this project. Each note is a single",
        "Markdown file with YAML front matter, suitable for shelling into an Obsidian vault.",
        "",
        f"**Last updated:** {last_updated}",
        "",
        "## Index",
        "",
        "| Note | Area | Sources | Words |",
        "|---|---|---:|---:|",
    ]
    for title, fname, area, src, words in rows:
        out.append(f"| [{title}]({fname}) | {area} | {src} | {words:,} |")

    out += ["", "## Tag index", "", "| Tag | Notes | Members |", "|---|---:|---|"]
    for tag in sorted(tags):
        members = ", ".join(f"[{m}]({m})" for m in sorted(tags[tag]))
        out.append(f"| `#{tag}` | {len(tags[tag])} | {members} |")

    out += [
        "",
        "## Conventions",
        "",
        "- **Filename** — lowercase kebab-case with a `.md` extension.",
        "- **Front matter** — `title`, `description`, `tags`, `supabase_area`, `doc_kind`,",
        "  `status`, `owner`, `last_reviewed`, `review_frequency`, `source`.",
        "- **Tags** — hierarchical `knowledge/<value>` (see `tags` above).",
        "- **Citations** — each note ends with a `การอ้างอิง:` block listing numbered",
        "  `[n] Title URL` entries; inline markers `[n]` refer to it. Preserve both.",
        "- **Never** put credentials, client secrets, tokens, or private keys in a note.",
        "",
        "> This index is generated — run `python3 knowledge/build_knowledge_readme.py`",
        "> after adding or editing a note. `--check` verifies it in CI.",
        "",
    ]
    new = "\n".join(out)

    if args.check:
        if new != current:
            print("[readme] OUT OF DATE — run build_knowledge_readme.py", file=sys.stderr)
            return 1
        print("[readme] up to date")
        return 0

    README.write_text(new, encoding="utf-8")
    print(f"[readme] wrote {README} — {len(notes)} note(s), {len(tags)} tag(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
