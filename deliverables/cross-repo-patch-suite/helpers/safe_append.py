#!/usr/bin/env python3
"""Helper — append to a file without disturbing a byte of what is already there.

Thin wrapper over :mod:`patchsuite` for the case you actually hit: adding a
section to a file that already exists, in a repo where that file's line endings
differ from yours.

    python helpers/safe_append.py CONTRIBUTING.md --text "## Tests\\nRun pytest."
    python helpers/safe_append.py CONTRIBUTING.md --text-file snippet.md --apply
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from patchsuite import append_text, diff_stat, safe_read, verify_append  # noqa: E402


def run(
    target: Path,
    payload: str,
    *,
    align: bool = True,
    apply: bool = False,
) -> dict[str, object]:
    before = safe_read(target)
    result = append_text(target, payload, align=align, dry_run=not apply)
    after = safe_read(target)
    verification = verify_append(before, after if apply else before)
    return {
        "path": str(target),
        "mode": "applied" if apply else "dry-run",
        "bytes_before": len(before),
        "bytes_after": len(after) if apply else result.bytes_after,
        "existing_eol": result.existing_eol,
        "terminator_added": result.terminator_added,
        "diff": diff_stat(before, after if apply else before),
        "prefix_preserved": verification.prefix_identical if apply else True,
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "safe": (verification.ok if apply else True),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="literal text to append")
    group.add_argument("--text-file", help="read the payload from this file")
    parser.add_argument("--no-align", action="store_true", help="do not match the target's endings")
    parser.add_argument("--apply", action="store_true", help="write (default is a dry run)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = args.text if args.text is not None else Path(args.text_file).read_text(encoding="utf-8")
    report = run(Path(args.file), payload, align=not args.no_align, apply=args.apply)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
        if not args.apply:
            print("\nDry run — nothing was written. Re-run with --apply to commit the change.")

    return 0 if report["safe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
