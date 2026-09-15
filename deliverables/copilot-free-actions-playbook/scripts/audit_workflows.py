#!/usr/bin/env python3
"""
audit_workflows.py — static audit of GitHub Actions workflows.

Checks every workflow YAML against the hardening rules from the
Copilot Free + Actions playbook:

  1. unpinned-action   : `uses:` on a moving tag (@v4, @main) instead of a full SHA
  2. broad-permissions : no top-level `permissions:` block (inherits org default)
  3. injection-risk    : `${{ github.* }}` used directly inside a `run:` block
  4. no-timeout        : a job without `timeout-minutes:`
  5. no-concurrency    : workflow without a `concurrency:` block
  6. long-retention    : upload-artifact without `retention-days:`

Usage:
    python audit_workflows.py <path-to-.github/workflows>
    python audit_workflows.py .github/workflows --json report.json

Exit code is 1 when any ERROR-level finding is present, else 0.
No third-party dependencies — stdlib only, so it runs anywhere.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*-?\s*uses:\s*(\S+)")
RUN_RE = re.compile(r"^\s*run:\s*(\||>)?(.*)$")
TIMEOUT_RE = re.compile(r"^\s*timeout-minutes:\s*\d+")
CONCURRENCY_RE = re.compile(r"^concurrency:")
PERMISSIONS_RE = re.compile(r"^permissions:")
RETENTION_RE = re.compile(r"^\s*retention-days:\s*\d+")
UPLOAD_ARTIFACT_RE = re.compile(r"uses:\s*actions/upload-artifact@")
GITHUB_EXPR_RE = re.compile(r"\$\{\{\s*github\.[a-zA-Z_.]+")

ERROR, WARN = "ERROR", "WARN"


def _is_local_uses(ref: str) -> bool:
    """./path, docker://, or a reusable workflow in the same repo."""
    return ref.startswith("./") or ref.startswith("docker://")


def _pin_state(ref: str) -> tuple[bool, str]:
    """Return (is_pinned, detail) for a `uses:` reference."""
    if "@" not in ref:
        return False, "no @ref at all"
    _, _, version = ref.rpartition("@")
    if SHA_RE.match(version.strip()):
        return True, version.strip()
    if version.strip().startswith("v") and version.strip()[1:].isdigit():
        # A bare @vN is a moving tag. A line ending in `# vN` is the pinned form
        # (checked by the caller against the raw line, not the parsed ref).
        return False, f"moving tag @{version.strip()}"
    return False, f"non-SHA ref @{version.strip()}"


def audit_file(path: pathlib.Path) -> list[dict]:
    findings: list[dict] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    has_top_permissions = False
    has_concurrency = False
    in_run_block = False
    run_indent = 0
    in_jobs = False          # only keys under `jobs:` are jobs — `on:` triggers are not
    job_has_timeout = False
    current_job: str | None = None
    seen_jobs: list[tuple[str, bool]] = []
    in_upload_step = False
    upload_has_retention = False
    upload_line = 0

    def flush_job() -> None:
        if current_job is not None:
            seen_jobs.append((current_job, job_has_timeout))

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # --- run-block tracking (to catch injection inside run:) -------------
        if in_run_block:
            stripped = line.strip()
            if stripped and (len(line) - len(line.lstrip())) <= run_indent:
                in_run_block = False  # dedented — block ended
            else:
                m = GITHUB_EXPR_RE.search(line)
                if m:
                    findings.append({
                        "line": idx, "level": ERROR, "rule": "injection-risk",
                        "detail": f"{m.group(0)} used inside a run: block — route it via env:",
                        "text": stripped[:120],
                    })
                continue

        rm = RUN_RE.match(line)
        if rm:
            inline = rm.group(2)
            if inline:  # `run: echo "${{ github.x }}"` on one line
                m = GITHUB_EXPR_RE.search(inline)
                if m:
                    findings.append({
                        "line": idx, "level": ERROR, "rule": "injection-risk",
                        "detail": f"{m.group(0)} used inside a run: block — route it via env:",
                        "text": line.strip()[:120],
                    })
            else:  # block scalar — track the following indented lines
                in_run_block = True
                run_indent = len(line) - len(line.lstrip())
            continue

        # --- workflow-level blocks ------------------------------------------
        if PERMISSIONS_RE.match(line):
            has_top_permissions = True
        if CONCURRENCY_RE.match(line):
            has_concurrency = True

        # --- job boundaries (only keys under a top-level `jobs:`) -------------
        if line and not line[0].isspace() and line.rstrip().endswith(":"):
            in_jobs = line.strip() == "jobs:"
            if not in_jobs:
                flush_job()
                current_job = None
        jm = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line) if in_jobs else None
        if jm:
            flush_job()
            current_job, job_has_timeout = jm.group(1), False
        if TIMEOUT_RE.match(line):
            job_has_timeout = True

        # --- action pinning ---------------------------------------------------
        um = USES_RE.match(line)
        if um:
            ref = um.group(1).strip().strip("'\"")
            if not _is_local_uses(ref):
                if UPLOAD_ARTIFACT_RE.search(line):
                    in_upload_step, upload_has_retention, upload_line = True, False, idx
                pinned, detail = _pin_state(ref)
                # `uses: owner/action@<sha>  # v4` is the correct pinned form
                has_trailing_tag = "#" in line and SHA_RE.match(
                    ref.rpartition("@")[2].strip()
                ) is not None
                if not pinned and not has_trailing_tag:
                    findings.append({
                        "line": idx, "level": ERROR, "rule": "unpinned-action",
                        "detail": f"{ref} ({detail}) — pin to a full 40-char SHA",
                        "text": line.strip()[:120],
                    })
            else:
                in_upload_step = False

        # --- artifact retention ----------------------------------------------
        if in_upload_step:
            if RETENTION_RE.match(line):
                upload_has_retention = True
            elif len(line) - len(line.lstrip()) <= 6 and line.strip().startswith("-"):
                if not upload_has_retention:
                    findings.append({
                        "line": upload_line, "level": WARN, "rule": "long-retention",
                        "detail": "upload-artifact without retention-days (default 90 days)",
                        "text": line.strip()[:120],
                    })
                in_upload_step = False

    flush_job()

    # --- workflow-level findings ---------------------------------------------
    if not has_top_permissions:
        findings.append({
            "line": 1, "level": ERROR, "rule": "broad-permissions",
            "detail": "no top-level permissions: block — inherits the org default",
            "text": "(workflow)",
        })
    if not has_concurrency:
        findings.append({
            "line": 1, "level": WARN, "rule": "no-concurrency",
            "detail": "no concurrency: block — redundant runs are not cancelled",
            "text": "(workflow)",
        })

    # --- per-job findings -----------------------------------------------------
    job_header_lines = {}
    for idx, line in enumerate(lines, start=1):
        jm = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if jm:
            job_header_lines[jm.group(1)] = idx
    for job, has_timeout in seen_jobs:
        if not has_timeout and job not in ("permissions", "on", "env"):
            findings.append({
                "line": job_header_lines.get(job, 1), "level": WARN,
                "rule": "no-timeout",
                "detail": f"job '{job}' has no timeout-minutes: — cap the worst case",
                "text": f"jobs.{job}",
            })

    return sorted(findings, key=lambda f: f["line"])


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit GitHub Actions workflows for hardening gaps.")
    ap.add_argument("workflow_dir", help="path to .github/workflows")
    ap.add_argument("--json", metavar="PATH", help="also write a JSON report here")
    args = ap.parse_args()

    root = pathlib.Path(args.workflow_dir)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix in (".yml", ".yaml")
    )
    if not files:
        print(f"no workflow files found under {root}")
        return 0

    report, errors, warns = {}, 0, 0
    for f in files:
        fnd = audit_file(f)
        if fnd:
            report[str(f.relative_to(root))] = fnd
        errors += sum(1 for x in fnd if x["level"] == ERROR)
        warns += sum(1 for x in fnd if x["level"] == WARN)

    for name, fnd in report.items():
        print(f"\n{name}")
        for x in fnd:
            print(f"  {x['line']:>4}  {x['level']:<5} {x['rule']:<18} {x['detail']}")

    print(f"\n{'-' * 68}")
    print(f"files scanned : {len(files)}")
    print(f"findings      : {errors} error, {warns} warn")
    print(f"clean files   : {len(files) - len(report)}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"summary": {"files": len(files), "errors": errors,
                                    "warnings": warns}, "findings": report},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"json report   : {args.json}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
