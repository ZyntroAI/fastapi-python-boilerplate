#!/usr/bin/env python3
"""Tests for verify_workflows.py's SHA resolution.

This exists because the first release of the verifier shipped a resolver that
reported *every* pin as non-existent, so the check was worse than useless: it
would have failed CI on a correct tree. Two distinct bugs produced that, and
each has a case below.

    python deliverables/ci/test_verify_workflows.py

Needs network (it resolves real refs). Exits non-zero on any failure.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verify_workflows", HERE / "verify_workflows.py")
vw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vw)

# (action ref, sha, expected, why this case is here)
CASES = [
    # --- real commits must resolve -------------------------------------------
    ("actions/checkout",
     "11bd71901bbe5b1630ceea73d27597364c9af683", True,
     "annotated tag v4.2.2 -- commit hash appears only on the peeled ^{} line"),
    ("actions/checkout",
     "11d5960a326750d5838078e36cf38b85af677262", True,
     "annotated tag v4 -- a different release of the same action"),
    ("somaz94/compress-decompress",
     "4aa7a81b5e2c20ac4a865d937466f3d8928f487c", True,
     "lightweight tag v1 -- commit has no peeled line"),
    ("subosito/flutter-action",
     "1a449444c387b1966244ae4d4f8c696479add0b2", True,
     "lightweight tag v2"),
    ("wzieba/Firebase-Distribution-Github-Action",
     "bd494989dd4bec0343f78adee87fe66e48279ad6", True,
     "lightweight tag v1"),
    ("release-drafter/release-drafter",
     "6a93d829887aa2e0748befe2e808c66c0ec6e4c7", True,
     "annotated tag v6, peeled -- regression guard for the --refs bug"),
    ("release-drafter/release-drafter",
     "67e173cadb2fbd3de94f4a861e0c48c913b462ae", True,
     "the tag object itself is also a legitimate ref value"),

    # --- fabrications must NOT resolve ---------------------------------------
    ("actions/checkout",
     "f548e57c3d3c42e288026812cd22362661c4e8d4", False,
     "the fabricated SHA that was live on main and broke every CI job"),
    ("actions/checkout",
     "0000000000000000000000000000000000000000", False,
     "all-zeroes"),
    ("actions/checkout/fake-subpath",
     "f548e57c3d3c42e288026812cd22362661c4e8d4", False,
     "same fabrication behind a subpath -- repo_of() must strip it"),
    ("actions/checkout",
     "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", False,
     "well-formed hex that names nothing"),
]


def main() -> int:
    # fail fast if the network is unavailable, rather than reporting everything fake
    try:
        import subprocess
        r = subprocess.run(
            ["git", "ls-remote", "--heads", "https://github.com/actions/checkout"],
            capture_output=True, text=True, env=vw.LS_ENV, timeout=30,
        )
        if r.returncode != 0 or not r.stdout.strip():
            print("SKIP — cannot reach github.com; SHA cases need network")
            return 0
    except Exception as exc:  # noqa: BLE001
        print(f"SKIP — network unavailable ({exc})")
        return 0

    print(f"{'action ref':<46} {'sha':<14} {'want':<6} {'got':<6} ok")
    print("-" * 88)
    failed = 0
    for action, sha, want, why in CASES:
        got = vw.real_sha(action, sha)
        ok = got == want
        failed += 0 if ok else 1
        print(f"{action:<46} {sha[:12]:<14} {str(want):<6} {str(got):<6} "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            print(f"    ^ {why}")

    print()
    # shape helpers that need no network
    assert vw.repo_of("github/codeql-action/init") == "github/codeql-action"
    assert vw.repo_of("actions/checkout") == "actions/checkout"
    print("repo_of() subpath handling: PASS")

    if failed:
        print(f"\n{failed}/{len(CASES)} SHA case(s) FAILED")
        return 1
    print(f"\nALL {len(CASES)} SHA CASES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
