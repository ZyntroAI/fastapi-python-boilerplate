#!/usr/bin/env python3
"""Generate the suite's fixtures as exact bytes.

Real fixures must be byte-precise — a CRLF file written through text mode is an
LF file, and the whole point of the broken fixture is that its endings are what
they are. Everything here is written with ``write_bytes``.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE_ROOT = HERE.parent
FIXTURES = SUITE_ROOT / "fixtures"


def w(path: Path, text: str, *, crlf: bool = False, final_newline: bool = True) -> None:
    """Write ``text`` with the requested endings, byte-exactly."""
    body = text.replace("\r\n", "\n").replace("\r", "\n")
    data = body.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    if final_newline and not data.endswith(b"\n"):
        data += b"\r\n" if crlf else b"\n"
    if not final_newline and data.endswith(b"\n"):
        data = data[:-1]
        if crlf and data.endswith(b"\r"):
            data = data[:-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# --------------------------------------------------------------------------
# clean-project — everything already correct
# --------------------------------------------------------------------------

CLEAN_WORKFLOW = """\
name: Quality Gate

on:
  pull_request:

permissions:
  contents: read

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - name: Set up Python
        uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b
        with:
          python-version: "3.12"
      - name: Run the gate
        run: python -m pytest -q
"""

CLEAN_README = """\
# Clean project

A fixture whose files are already in the state the suite enforces: LF endings,
trailing newlines, parseable workflows, and SHA-pinned actions.
"""

CLEAN_CHANGELOG = """\
# Changelog

## 0.1.0

- Initial release.
"""

CLEAN_CONTRIBUTING = """\
# Contributing

Run the test suite before opening a pull request.
"""


def build_clean() -> None:
    root = FIXTURES / "clean-project"
    w(root / "README.md", CLEAN_README)
    w(root / ".github/workflows/quality-gate.yml", CLEAN_WORKFLOW)
    w(root / "notes/CHANGELOG.md", CLEAN_CHANGELOG)
    w(root / "notes/CONTRIBUTING.md", CLEAN_CONTRIBUTING)
    w(root / "src/app.py", '"""Fixture module."""\n\n\ndef main() -> int:\n    return 0\n')


# --------------------------------------------------------------------------
# broken-project — each file embodies one failure mode
# --------------------------------------------------------------------------

# CRLF *and* no trailing newline: `git am` says "patch does not apply" while
# `git apply --check` passes. This is the combination that misleads debugging.
BROKEN_CRLF_WORKFLOW = """\
name: Legacy Sync

on:
  push:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: echo "syncing"
"""

# Unquoted colon inside a scalar: a ScannerError, not a mapping error.
BROKEN_UNQUOTED_COLON = """\
name: Report

on:
  workflow_dispatch:

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: :x:
        run: echo "broken"
"""

# Parseable, but a mix of pinned and unpinned action references.
BROKEN_MIXED_PINS = """\
name: Mixed Pins

on:
  push:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
      - uses: actions/cache@v4
      - uses: actions/upload-artifact@v4
"""

BROKEN_README = """\
# Broken project

A fixture that reproduces, file by file, the failures the suite is built to
catch. Do not treat any of these files as examples to copy.
"""


def build_broken() -> None:
    root = FIXTURES / "broken-project"
    w(root / "README.md", BROKEN_README)

    # 1. CRLF without a trailing newline.
    w(
        root / ".github/workflows/crlf-unterminated.yml",
        BROKEN_CRLF_WORKFLOW,
        crlf=True,
        final_newline=False,
    )

    # 2. Unparseable YAML from an unquoted colon.
    w(root / ".github/workflows/unquoted-colon.yml", BROKEN_UNQUOTED_COLON)

    # 3. Partially pinned action references (parses fine, fails the pin audit).
    w(root / ".github/workflows/mixed-refs.yml", BROKEN_MIXED_PINS)

    # 4. A CRLF document *with* a trailing newline — patches must keep it CRLF.
    w(
        root / "notes/CONTRIBUTING.md",
        "# Contributing\r\n\r\nThis file is CRLF and must stay CRLF.\r\n",
        crlf=True,
    )

    # 5. Mixed endings — the append path resolves to the majority terminator.
    mixed = root / "notes/legacy.txt"
    mixed.parent.mkdir(parents=True, exist_ok=True)
    mixed.write_bytes(b"first line\r\nsecond line\nthird line\r\nfourth line\r\n")

    w(root / "src/app.py", '"""Broken fixture module."""\n\n\ndef run() -> None:\n    pass\n')


def main() -> int:
    if FIXTURES.exists():
        shutil.rmtree(FIXTURES)
    build_clean()
    build_broken()
    total = sum(1 for _ in FIXTURES.rglob("*") if _.is_file())
    print(f"Wrote {total} fixture files under {FIXTURES.relative_to(SUITE_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
