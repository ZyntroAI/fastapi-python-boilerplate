#!/usr/bin/env python3
"""
Extract metadata & content from docs/ folder → JSON index
Usage: python scripts/extract_metadata.py docs/ > repo_index.json
"""

import sys
import os
import json
import re
from pathlib import Path

def extract_markdown_content(file_path):
    """Extract title, headings, and plain text from .md file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

    # Extract first H1 as title
    title = "Untitled"
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()

    # Extract headings
    headings = re.findall(r"^#{2,6}\s+(.+)$", content, re.MULTILINE)

    # Clean plain text (strip markdown syntax)
    text = re.sub(r"```[\s\S]*?```", " ", content)  # code blocks
    text = re.sub(r"`[^`]+`", " ", text)             # inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = re.sub(r"[*_~]{1,3}([^*_~]+)[*_~]{1,3}", r"\1", text)  # bold/italic
    text = re.sub(r"\s+", " ", text).strip()

    return {
        "title": title,
        "headings": headings,
        "content": text[:5000],  # limit length
        "word_count": len(text.split())
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_metadata.py <docs_root>", file=sys.stderr)
        sys.exit(1)

    docs_root = Path(sys.argv[1])
    if not docs_root.exists():
        print(f"Error: {docs_root} not found", file=sys.stderr)
        sys.exit(1)

    index = {
        "source": "repo-docs",
        "generated_at": None,
        "files": []
    }

    for md_file in sorted(docs_root.rglob("*.md")):
        rel_path = str(md_file.relative_to(docs_root))
        data = extract_markdown_content(md_file)
        if data:
            index["files"].append({
                "path": rel_path,
                **data
            })

    index["file_count"] = len(index["files"])
    print(json.dumps(index, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
