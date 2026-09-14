#!/usr/bin/env python3
"""
Push JSON index to Algolia search index.
Usage: python scripts/push_index.py <index_file.json>
Requires env: ALGOLIA_APP_ID, ALGOLIA_API_KEY
"""

import json
import os
import sys
from pathlib import Path

try:
    from algoliasearch.search_client import SearchClient
except ImportError:
    SearchClient = None
    print("⚠️ algoliasearch not installed — saving mock output only", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: push_index.py <index_file.json>", file=sys.stderr)
        sys.exit(1)

    index_path = Path(sys.argv[1])
    if not index_path.exists():
        print(f"❌ File not found: {index_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(index_path.read_text(encoding="utf-8"))
    app_id = os.getenv("ALGOLIA_APP_ID")
    api_key = os.getenv("ALGOLIA_API_KEY")
    index_name = os.getenv("ALGOLIA_INDEX_NAME", "docs_index")

    print(f"📄 Loaded: {data.get('count', 0)} records from {index_path.name}")

    if not app_id or not api_key or SearchClient is None:
        print("⚠️ Algolia credentials or library missing — index not pushed")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "\n...")
        return

    try:
        client = SearchClient.create(app_id, api_key)
        index = client.init_index(index_name)
        records = data.get("items", data) if isinstance(data, dict) else data
        index.save_objects(records)
        print(f"✅ Pushed {len(records)} records to Algolia index '{index_name}'")
    except Exception as e:
        print(f"❌ Algolia error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
