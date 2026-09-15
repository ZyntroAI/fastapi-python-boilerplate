#!/usr/bin/env python3
"""
test_audit_workflows.py — proves the audit rules fire on bad input and stay
quiet on good input. Run:  python3 scripts/test_audit_workflows.py
Exit 0 = all assertions pass.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from audit_workflows import audit_file  # noqa: E402

GOOD = """\
name: Good
on:
  pull_request:
permissions: {}
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - name: Safe
        env:
          BODY: ${{ github.event.pull_request.title }}
        run: echo "$BODY"
"""

BAD = """\
name: Bad
on:
  push:
permissions: {}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2
      - name: Dangerous
        run: echo "${{ github.event.issue.body }}"
      - uses: actions/upload-artifact@v4
        with:
          name: out
          path: dist/
"""


def rules(findings, path_filter=None):
    return sorted({f["rule"] for f in findings})


def main() -> int:
    ok = True
    tmp = pathlib.Path(tempfile.mkdtemp())

    good = tmp / "good.yml"
    good.write_text(GOOD, encoding="utf-8")
    g_res = rules(audit_file(good))
    print(f"GOOD file findings: {g_res or 'none'}")
    if g_res:
        print("  FAIL: a clean workflow should produce no findings")
        ok = False

    bad = tmp / "bad.yml"
    bad.write_text(BAD, encoding="utf-8")
    b_res = audit_file(bad)
    b_rules = rules(b_res)
    print(f"BAD  file findings: {b_rules}")

    expected = {"unpinned-action", "injection-risk", "no-timeout", "no-concurrency",
                "long-retention"}
    missing = expected - set(b_rules)
    if missing:
        print(f"  FAIL: rules did not fire: {sorted(missing)}")
        ok = False

    # injection must be parsed from INSIDE run:, and github.event used via env:
    # in the GOOD file must NOT be flagged.
    if any(f["rule"] == "injection-risk" for f in audit_file(good)):
        print("  FAIL: env-routed github expression wrongly flagged")
        ok = False

    # `on: push` must not be counted as a job missing a timeout
    bad_jobs = {f["text"] for f in b_res if f["rule"] == "no-timeout"}
    if not any("build" in t for t in bad_jobs):
        print("  FAIL: real job 'build' not checked for timeout")
        ok = False
    if any("push" in t for t in bad_jobs):
        print("  FAIL: 'on: push' trigger wrongly treated as a job")
        ok = False

    print("\n" + ("PASS — all assertions hold" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
