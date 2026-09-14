#!/usr/bin/env python3
"""Offline validator for the Full CI/CD Pipeline deliverable.

Checks, in order:
  1. every workflow file parses as YAML
  2. zero unpinned ``uses:`` refs (all must be 40-char commit SHAs)
  3. declared job graph is internally consistent (``needs`` targets exist, acyclic)
  4. the gate job aggregates every real job

Exit code 0 = READY, 1 = findings. Usage:  python validate_pipeline.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: python -m pip install pyyaml")

HERE = Path(__file__).resolve().parent
WF_DIR = HERE / ".github" / "workflows"
SHA_RE = re.compile(r"^[^@\s]+@([0-9a-f]{40})$")
USES_RE = re.compile(r"uses:\s*([^\s#]+)")

findings: list[str] = []


def check_yaml(path: Path) -> dict | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        findings.append(f"[yaml] {path.name}: {str(exc).splitlines()[0][:90]}")
        return None


def check_pins(path: Path) -> tuple[int, list[str]]:
    total = 0
    bad: list[str] = []
    for ref in USES_RE.findall(path.read_text(encoding="utf-8")):
        if ref.startswith("./"):
            continue  # local reusable workflow -- no SHA needed
        total += 1
        if not SHA_RE.match(ref):
            bad.append(ref)
    return total, bad


def _needs(spec: dict) -> list[str]:
    """Normalise `needs:` which may be a string or a list."""
    raw = (spec or {}).get("needs")
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    return list(raw)


def check_graph(doc: dict, path: Path) -> None:
    jobs = doc.get("jobs") or {}
    if not isinstance(jobs, dict):
        findings.append(f"[graph] {path.name}: jobs is not a mapping")
        return
    for job, spec in jobs.items():
        for need in _needs(spec):
            if need not in jobs:
                findings.append(
                    f"[graph] {path.name}: job '{job}' needs unknown '{need}'"
                )

    seen: set[str] = set()
    stack: set[str] = set()

    def visit(n: str) -> None:
        if n in stack:
            findings.append(f"[graph] {path.name}: cycle through '{n}'")
            return
        if n in seen:
            return
        stack.add(n)
        for need in _needs(jobs.get(n)):
            if need in jobs:
                visit(need)
        stack.discard(n)
        seen.add(n)

    for job in jobs:
        visit(job)

    if "ci-gate" in jobs:
        gate = set(_needs(jobs["ci-gate"]))
        real = {j for j in jobs if j != "ci-gate"}
        missing = real - gate
        if missing:
            findings.append(
                f"[gate] pipeline.yml: ci-gate does not aggregate {sorted(missing)}"
            )


def main() -> int:
    files = sorted(WF_DIR.glob("*.yml"))
    if not files:
        sys.exit(f"no workflow files found under {WF_DIR}")

    print("Full CI/CD Pipeline -- validation\n" + "-" * 44)
    for path in files:
        doc = check_yaml(path)
        total, bad = check_pins(path)
        tag = "OK " if doc is not None and not bad else "ERR"
        print(f"{tag} {path.name:32s} refs={total:>2} unpinned={len(bad)}")
        for ref in bad:
            findings.append(f"[pin] {path.name}: unpinned '{ref}'")
        if doc is not None:
            check_graph(doc, path)

    print("-" * 44)
    if findings:
        print(f"FINDINGS ({len(findings)}):")
        for f in findings:
            print("  -", f)
        return 1
    print("READY -- all files parse, all refs pinned, job graph consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
