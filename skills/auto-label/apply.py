#!/usr/bin/env python3
"""Apply labels to a PR using the auto-label classifier.

Dry-run by default. Pass --apply to actually write. This mirrors the
convention used by every other script in this repo.

    # show what PR #293 would get
    python apply.py --repo OWNER/REPO --pr 293

    # apply it
    python apply.py --repo OWNER/REPO --pr 293 --apply

Reads via `gh`, which must be authenticated. Applying labels is a WRITE to a
resource the user owns and is therefore gated behind the explicit flag, and
never removes a label a human set.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classify import classify, load_rules  # noqa: E402


def gh(args, check=True) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"gh {' '.join(args[:3])} failed ({proc.returncode})")
    return proc.stdout


def fetch_pr(repo: str, number: int) -> dict:
    raw = gh([
        "pr", "view", str(number), "--repo", repo,
        "--json", "title,labels,files,isDraft,state",
    ])
    data = json.loads(raw)
    data["paths"] = [f["path"] for f in data.get("files", [])]
    data["existing"] = [lbl["name"] for lbl in data.get("labels", [])]
    return data


def add_labels(repo: str, number: int, labels) -> None:
    for label in sorted(labels):
        gh(["pr", "edit", str(number), "--repo", repo, "--add-label", label])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Auto-label a PR (dry-run by default).")
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--pr", type=int, required=True, help="PR number")
    ap.add_argument("--apply", action="store_true", help="actually write the labels")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    info = fetch_pr(args.repo, args.pr)
    wanted = classify(info["title"], info["paths"], load_rules())

    existing = set(info["existing"])
    to_add = wanted - existing        # additive only: never compute a removal
    already = wanted & existing

    if args.json:
        print(json.dumps({
            "repo": args.repo, "pr": args.pr, "title": info["title"],
            "state": info["state"], "draft": info["isDraft"],
            "matched": sorted(wanted), "already": sorted(already),
            "to_add": sorted(to_add), "applied": bool(args.apply),
        }, ensure_ascii=False, indent=2))
    else:
        print(f"{args.repo} PR #{args.pr} — {info['title']}")
        print(f"  files: {len(info['paths'])}")
        if already:
            print(f"  already has: {', '.join(sorted(already))}")
        if not wanted:
            print("  no rule matched — leaving unlabelled (by design)")
        elif not to_add:
            print("  nothing to add")
        else:
            verb = "adding" if args.apply else "would add"
            print(f"  {verb}: {', '.join(sorted(to_add))}")

    if args.apply and to_add:
        add_labels(args.repo, args.pr, to_add)
        if not args.json:
            print(f"  ✅ applied {len(to_add)} label(s)")
    elif to_add and not args.apply:
        if not args.json:
            print("  (dry-run — re-run with --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
