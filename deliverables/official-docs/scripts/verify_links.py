#!/usr/bin/env python3
"""Re-check every URL in the registry with a live HTTP request.

Run:  python scripts/verify_links.py [--timeout 20] [--json]

Exit codes:
  0 — every URL answered 2xx/3xx
  1 — at least one URL failed (the failing list is printed)
  2 — the registry JSON is missing (run export_registry.mjs first)

This is the CI gate. It deliberately does NOT follow redirects into a 200 and
call it healthy: a 404 or a dead host is reported as-is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from official_docs import load_registry  # noqa: E402

USER_AGENT = "ZyntroAI-official-docs-linkcheck/1.2"


def check(url: str, timeout: int) -> tuple[int, str]:
    """Return (status_code, note). status 0 means the request never completed."""
    request = Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    opener = build_opener()
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, "ok"
    except HTTPError as exc:
        return exc.code, f"HTTP {exc.code}"
    except URLError as exc:
        return 0, f"unreachable: {exc.reason}"
    except Exception as exc:  # pragma: no cover - defensive
        return 0, f"error: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify official documentation links")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    try:
        registry = load_registry()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    results = []
    failures = []
    for group_key, group_name, link_label, url in registry.iter_links():
        status, note = check(url, args.timeout)
        healthy = 200 <= status < 400
        results.append(
            {
                "group": group_key,
                "name": group_name,
                "label": link_label,
                "url": url,
                "status": status,
                "note": note,
                "healthy": healthy,
            }
        )
        if not healthy:
            failures.append(results[-1])

    if args.json:
        print(json.dumps({"checked": len(results), "failed": len(failures), "results": results}, indent=2))
    else:
        for item in results:
            mark = "OK  " if item["healthy"] else "FAIL"
            print(f"{mark} {item['status']:>4}  {item['url']}")

    if failures:
        print(f"\n{len(failures)} of {len(results)} link(s) failed:", file=sys.stderr)
        for item in failures:
            print(f"  - {item['url']} ({item['note']})", file=sys.stderr)
        return 1

    print(f"\nAll {len(results)} links healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
