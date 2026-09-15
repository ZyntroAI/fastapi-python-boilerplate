#!/usr/bin/env python3
"""FIG best-practices quality gate — CLI entry point.

    python quality_gate.py --root /path/to/project
    python quality_gate.py --root . --json
    python quality_gate.py --list
    python quality_gate.py --policy policy/fig-best-practices.yaml --root .

Exit codes:
    0  every blocking criterion passed
    1  at least one blocking criterion failed
    2  the policy could not be loaded or is structurally invalid
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figbp import load_policy, run_gate  # noqa: E402

PASS = "PASS"
FAIL = "FAIL"


def _print_report(report, stream=None) -> None:
    # Resolved at call time: binding sys.stdout as a default argument freezes it
    # at import, so a caller that replaces sys.stdout captures nothing.
    if stream is None:
        stream = sys.stdout
    width = max((len(r.id) for r in report.results), default=8)
    for result in report.results:
        mark = PASS if result.passed else FAIL
        line = f"{mark}  {result.id.ljust(width)}  {result.summary}"
        print(line, file=stream)
        for item in result.evidence:
            print(f"      - {item}", file=stream)

    print("", file=stream)
    if report.passed:
        print(f"{report.score} criteria passed — safe to deploy.", file=stream)
    else:
        failed = ", ".join(r.id for r in report.blocking_failures)
        print(f"{report.score} criteria passed — BLOCKED by: {failed}", file=stream)
    for advisory in report.advisories:
        print(f"advisory: {advisory.id} — {advisory.summary}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="quality_gate",
        description="Enforce the FIG / hellofig.ai best-practices standard.",
    )
    parser.add_argument("--root", default=".", help="project directory to check")
    parser.add_argument("--policy", default=None, help="path to the policy YAML")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--list", action="store_true", dest="list_criteria", help="list criteria and exit")
    parser.add_argument(
        "--fail-on-advisory", action="store_true", help="treat advisory failures as blocking"
    )
    args = parser.parse_args(argv)

    try:
        policy = load_policy(args.policy)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - surface any parse failure distinctly
        print(f"ERROR: could not parse policy: {exc}", file=sys.stderr)
        return 2

    if policy.errors:
        print("ERROR: policy is structurally invalid:", file=sys.stderr)
        for error in policy.errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    if args.list_criteria:
        for criterion in policy.criteria:
            print(f"{criterion['id']}  [{criterion['severity']}]  {criterion['description']}")
        return 0

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: --root is not a directory: {root}", file=sys.stderr)
        return 2

    report = run_gate(policy, root)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_report(report)

    if report.passed:
        return 0
    if args.fail_on_advisory and report.advisories:
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
