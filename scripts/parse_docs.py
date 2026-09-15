#!/usr/bin/env python3
"""
Parse HTML documentation → simplified markdown index
Usage: python scripts/parse_docs.py input.html > output.md
"""

import sys
import re
from html.parser import HTMLParser

class DocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_title = False
        self.in_body = False
        self.skip_tags = ("script", "style", "nav", "header", "footer")
        self.skip_level = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip_level += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li"):
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip_level -= 1

    def handle_data(self, data):
        if self.skip_level > 0:
            return
        text = data.strip()
        if text:
            self.text_parts.append(text + " ")

def main():
    if len(sys.argv) < 2:
        print("# Policy Snapshot\n\nSource: stdin\n")
        print("No input file provided.")
        return

    source_path = sys.argv[1]
    print(f"# Policy Snapshot\n\nSource: {source_path}\n\n")

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        html = source_path  # fallback
        print(f"⚠️ Could not read file: {e}\n\n")

    # Strip script/style/nav blocks quickly
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)

    parser = DocParser()
    parser.feed(html)
    parser.close()

    text = re.sub(r"\s+", " ", "".join(parser.text_parts)).strip()
    print(text[:8000])  # limit output size

if __name__ == "__main__":
    main()
