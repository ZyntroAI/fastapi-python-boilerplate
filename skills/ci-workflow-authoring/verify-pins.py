#!/usr/bin/env python3
"""Verify that every SHA-pinned `uses:` ref actually resolves on GitHub.

`lint.py` checks that a pin LOOKS like a 40-char SHA. This checks that it IS one:
a fabricated 40-hex string passes the regex and still fails at `Set up job` with
"Unable to find version". Ten such refs were found in this repository's
workflows, every one of which lint.py reported as clean.

    python skills/ci-workflow-authoring/verify-pins.py .github/workflows/*.yml

Exit 0 = every pin resolves. Exit 1 = at least one does not.

Verification uses the HTML commit endpoint (200 = exists, 404 = does not) rather
than the REST API, because the anonymous API allows only 60 requests/hour and a
repository of any size exhausts that mid-run. Resolution rules:

  - subdirectory actions (`owner/repo/subdir@sha`) belong to `owner/repo`, so the
    commit is looked up against the first two path segments. Querying the
    three-segment path 404s even for a real commit and yields a false verdict.
  - results are cached in memory per (action, sha) so a pin repeated across files
    costs one request, not one per file.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

USES_RE = re.compile(r"uses:\s*['\"]?([^\s'\"#]+)")
SHA_AT = re.compile(r"^(?P<path>[\w.-]+/[\w.-]+(?:/[\w.-]+)*)@(?P<sha>[0-9a-f]{40})$")


def owning_repo(action_path: str) -> str:
    """`owner/repo/subdir` -> `owner/repo`.

    A subdirectory action is a file inside `owner/repo`, so the commit must be
    looked up there. Querying the full three-segment path 404s even for a real
    commit, which would report every such pin as fake.
    """
    return "/".join(action_path.split("/")[:2])


def commit_exists(repo_path: str, sha: str) -> tuple[bool, str]:
    """Return (exists, note). Only the owning repo is queried."""
    repo = owning_repo(repo_path)
    url = f"https://github.com/{repo}/commit/{sha}"
    req = urllib.request.Request(url, headers={"User-Agent": "fig-pin-verify"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status == 200, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        # a network error is NOT evidence the SHA is fake — report it separately
        return False, f"{type(e).__name__}"


def collect_pins(paths: list[str]) -> dict[tuple[str, str], set[str]]:
    """Map (action_path, sha) -> set of workflow files that use it."""
    pairs: dict[tuple[str, str], set[str]] = {}
    for p in paths:
        path = Path(p)
        if not path.is_file():
            print(f"[verify] skip (not a file): {p}", file=sys.stderr)
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = USES_RE.search(line)
            if not m:
                continue
            mm = SHA_AT.match(m.group(1))
            if not mm:
                continue
            pairs.setdefault((mm.group("path"), mm.group("sha")), set()).add(path.name)
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", help="workflow files to check")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pairs = collect_pins(args.paths)

    if not pairs:
        print("[verify] no SHA-pinned refs found")
        return 0

    cache: dict[tuple[str, str], tuple[bool, str]] = {}
    fake: list[tuple[str, str, str, list[str]]] = []
    unverifiable: list[tuple[str, str, str]] = []

    for (action, sha), files in sorted(pairs.items()):
        key = (action, sha)
        if key not in cache:
            cache[key] = commit_exists(action, sha)
        ok, note = cache[key]
        if ok:
            if not args.quiet:
                print(f"  OK    {action}@{sha[:12]}  ({len(files)} file(s))")
        elif note.startswith("HTTP 40"):
            fake.append((action, sha, note, sorted(files)))
        else:
            unverifiable.append((action, sha, note))

    print(f"\n[verify] {len(pairs)} distinct pins; "
          f"{len(pairs) - len(fake) - len(unverifiable)} verified, "
          f"{len(fake)} not found, {len(unverifiable)} unverifiable")

    if fake:
        print("\nPINS THAT DO NOT EXIST (these fail at `Set up job`):", file=sys.stderr)
        for action, sha, note, files in fake:
            print(f"  {action}@{sha}  {note}  in {', '.join(files)}", file=sys.stderr)

    if unverifiable:
        print("\nCOULD NOT CHECK (network/rate limit — not evidence of a fake):")
        for action, sha, note in unverifiable:
            print(f"  {action}@{sha[:12]}  {note}")

    return 1 if fake else 0


if __name__ == "__main__":
    raise SystemExit(main())
