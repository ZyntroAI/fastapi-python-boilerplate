#!/usr/bin/env python3
"""
Parse HTML document → clean markdown/text snapshot.
Usage: python scripts/parse_docs.py input.html > output.md
"""

import re
import sys
from datetime import datetime

def strip_html_tags(text: str) -> str:
    """Remove HTML tags while preserving structure."""
    text = re.sub(r"<style.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<h[1-6][^>]*>", lambda m: "\n" + "#" * int(m.group(0)[2]) + " ", text)
    text = re.sub(r"</p>|\n?<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text

def clean_whitespace(text: str) -> str:
    """Normalize whitespace and line breaks."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: parse_docs.py <input.html> [output.md]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    encoding = "utf-8"

    try:
        with open(input_path, "r", encoding=encoding, errors="replace") as f:
            html = f.read()
    except Exception as e:
        print(f"❌ Cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Parsed Document"

    # Parse content
    text = strip_html_tags(html)
    text = clean_whitespace(text)

    # Output as Markdown
    output = f"""---
title: {title}
source_file: {input_path}
generated: {datetime.utcnow().isoformat()}Z
---

# {title}

> Source: {input_path}
> Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

{text}
"""

    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)

if __name__ == "__main__":
    main()
