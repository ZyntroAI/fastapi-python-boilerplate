"""CLI for docs-verify.

    python scripts/verify_docs.py [--root PATH] [--json]

Exit code is 0 when every non-skipped check passes, 1 otherwise — usable as a
CI gate or a pre-commit hook.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from docs_verify import render, verify  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="verify_docs",
        description="Check that repository documentation still matches the tree.",
    )
    ap.add_argument("--root", default=None,
                    help="repository root (default: three levels above this script)")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable output")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]
    report = verify(root)

    if args.json:
        print(json.dumps({
            "root": str(root),
            "passed": report.passed,
            "checks": [{"name": c.name, "status": c.status, "detail": c.detail}
                       for c in report.checks],
        }, indent=2))
    else:
        print(f"docs-verify  root={root}")
        print(render(report))

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
