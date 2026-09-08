#!/usr/bin/env python3
"""
Extract metadata from docs/ folder → JSON index output.
Usage: python scripts/extract_metadata.py docs/ > repo_index.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def extract_frontmatter(content: str):
    """Extract YAML-like frontmatter from markdown files."""
    meta = {}
    if content.startswith("---"):
        lines = content.splitlines()
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_metadata.py <docs_directory>", file=sys.stderr)
        sys.exit(1)

    docs_dir = Path(sys.argv[1])
    if not docs_dir.exists():
        print(f"⚠️ Directory not found: {docs_dir}", file=sys.stderr)
        print("[]")
        return

    index = []
    for path in sorted(docs_dir.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
            stat = path.stat()
            meta = extract_frontmatter(content)

            index.append({
                "title": meta.get("title", path.stem.replace("-", " ").title()),
                "path": str(path.relative_to(docs_dir)),
                "relative_path": str(path.relative_to(docs_dir.parent)),
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size_bytes": stat.st_size,
                "summary": content[:200].replace("\n", " ").strip() + "..." if len(content) > 200 else content.strip(),
                "tags": meta.get("tags", "").split() if meta.get("tags") else [],
            })
        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}", file=sys.stderr)

    print(json.dumps({
        "source": "repo-docs",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(index),
        "items": index,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
