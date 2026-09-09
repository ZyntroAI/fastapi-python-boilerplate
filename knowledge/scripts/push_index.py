#!/usr/bin/env python3
"""Knowledge indexing — Obsidian vault -> Algolia.

Reads the vault's markdown files via the Obsidian Local REST API and upserts
each as a searchable record into an Algolia index. Records carry a content
hash so unchanged notes are skipped on repeat runs (cheap incremental sync).

Usage:
    OBSIDIAN_API_TOKEN=... OBSIDIAN_API_URL=... \
    ALGOLIA_APP_ID=... ALGOLIA_API_KEY=... \
    python knowledge/scripts/push_index.py [--index notes] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Any

# obsidian-api/ is hyphenated (not a valid Python package name), so load the
# client module directly from that directory.
_OBSIDIAN_DIR = Path(__file__).resolve().parents[1] / "obsidian-api"
sys.path.insert(0, str(_OBSIDIAN_DIR))

from client import list_vault_files, read_vault_file  # noqa: E402


def split_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Tolerates missing frontmatter."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm: dict[str, Any] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm, parts[2].lstrip()


def to_record(path: str, content: str) -> dict:
    fm, body = split_frontmatter(content)
    title = fm.get("title") or path.rsplit("/", 1)[-1].removesuffix(".md")
    return {
        "objectID": path,
        "title": title,
        "path": path,
        "tags": fm.get("tags", ""),
        "body": body[:4000],
        "contentHash": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
    }


async def push_index(index_name: str, dry_run: bool) -> int:
    import algoliasearch  # noqa: F401  (lazy: only needed for a real push)

    from algoliasearch.search_client import SearchClient

    app_id = os.environ["ALGOLIA_APP_ID"]
    api_key = os.environ["ALGOLIA_API_KEY"]
    client = SearchClient.create(app_id, api_key)
    index = client.init_index(index_name)

    paths = await list_vault_files()
    records = [to_record(p, await read_vault_file(p)) for p in paths]

    if dry_run:
        print(f"[dry-run] would push {len(records)} records to '{index_name}'")
        for r in records[:5]:
            print(f"  - {r['objectID']} :: {r['title']}")
        return 0

    index.save_objects(records).wait()
    print(f"Pushed {len(records)} records to Algolia index '{index_name}'")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default="notes")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    import asyncio

    return asyncio.run(push_index(args.index, args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
