#!/usr/bin/env python3
"""
pin_workflows.py — resolve every tag/branch action reference in
.github/workflows/*.yml to a full 40-character commit SHA, verified against
the action's own repository.

Usage:
    export GITHUB_TOKEN=...            # needs `repo` + `workflow` scope
    export GITHUB_REPOSITORY=owner/repo
    python pin_workflows.py            # rewrite files in place
    python pin_workflows.py --dry-run  # show what would change

Exit codes:
    0 — nothing to do, or all refs rewritten
    1 — an error occurred (unresolvable ref, missing config)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")
API = "https://api.github.com"

USE_PATTERN = re.compile(r"uses:\s*([\w-]+/[\w.-]+)@([^\s\"'#]+)")
SHA40 = re.compile(r"^[a-f0-9]{40}$")
DOCKER_OR_LOCAL = re.compile(r"^\s*uses:\s*(docker://|\./)")


def _token() -> str | None:
    return (
        os.getenv("GITHUB_TOKEN")
        or os.getenv("GH_TOKEN")
        or os.getenv("GH_ENTERPRISE_TOKEN")
    )


def api_get(path: str) -> dict:
    token = _token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "pin-workflows",
    }
    if token and not path.startswith("https://api.github.com/repos/") is False:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        import json

        return json.load(resp)


def resolve_sha(repo: str, ref: str) -> str | None:
    """Resolve a tag/branch to the commit SHA it points at."""
    try:
        return api_get(f"/repos/{repo}/commits/{ref}").get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def verify_sha(repo: str, sha: str) -> bool:
    """Confirm the SHA really exists in that repository (no API rate limit)."""
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
         f"https://github.com/{repo}/commit/{sha}"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() == "200"


def collect_refs(files: list[Path]) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            if DOCKER_OR_LOCAL.match(line):
                continue
            for repo, ref in USE_PATTERN.findall(line.split("#")[0]):
                if SHA40.match(ref):
                    continue
                refs.setdefault(repo, set()).add(ref)
    return refs


def main() -> int:
    ap = argparse.ArgumentParser(description="Pin GitHub Actions to full SHAs")
    ap.add_argument("--dry-run", action="store_true", help="preview only")
    args = ap.parse_args()

    if not WORKFLOWS_DIR.is_dir():
        print(f"error: {WORKFLOWS_DIR} not found", file=sys.stderr)
        return 1

    files = sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml"))
    if not files:
        print("No workflow files found.")
        return 0

    refs = collect_refs(files)
    if not refs:
        print("Every action reference is already pinned to a full SHA.")
        return 0

    print(f"Resolving {sum(len(v) for v in refs.values())} unpinned reference(s)...")
    replacements: dict[str, str] = {}
    failures: list[str] = []

    for repo, refset in sorted(refs.items()):
        for ref in sorted(refset):
            sha = resolve_sha(repo, ref)
            if not sha:
                failures.append(f"{repo}@{ref}")
                print(f"  FAIL  {repo}@{ref} (not found)")
                continue
            if not verify_sha(repo, sha):
                failures.append(f"{repo}@{ref}")
                print(f"  FAIL  {repo}@{ref} -> {sha} (commit does not exist)")
                continue
            replacements[f"{repo}@{ref}"] = f"{repo}@{sha}"
            print(f"  OK    {repo}@{ref} -> {sha[:12]}")
            time.sleep(0.2)

    if failures:
        print(f"\nerror: could not resolve {len(failures)} reference(s):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"\n[dry-run] {len(replacements)} replacement(s) would be applied.")
        return 0

    touched = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        updated = original
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != original:
            f.write_text(updated, encoding="utf-8")
            touched += 1

    print(f"\nUpdated {touched} file(s). Review with `git diff` and commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
