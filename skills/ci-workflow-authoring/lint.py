"""Validate a workflow YAML the way GitHub Actions actually reads it.

An LLM-authored workflow often looks fine as text but is not valid YAML, or is
valid YAML that GitHub would reject. This checks both layers.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REQUIRED_ON = {"push", "pull_request", "workflow_dispatch", "schedule", "workflow_run"}


def check(path: Path) -> list[str]:
    problems: list[str] = []
    raw = path.read_text(encoding="utf-8")

    # 1. Does it even parse?
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        line = getattr(getattr(e, "problem_mark", None), "line", None)
        where = f" (around line {line + 1})" if line is not None else ""
        return [f"NOT VALID YAML{where}: {str(e).splitlines()[0]}"]

    if not isinstance(doc, dict):
        return ["top level is not a mapping"]

    # PyYAML resolves the bare key `on:` to boolean True (YAML 1.1). Accept both
    # spellings, otherwise every valid workflow reports a missing `on`.
    has_on = "on" in doc or True in doc

    # 2. Required top-level keys
    for key in ("name", "jobs"):
        if key not in doc:
            problems.append(f"missing required top-level key: {key}")
    if not has_on:
        problems.append("missing required top-level key: on")
    if "jobs" not in doc:
        return problems

    # 3. Every job must be runnable
    for job_name, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            problems.append(f"job '{job_name}' is not a mapping")
            continue
        if "runs-on" not in job:
            problems.append(f"job '{job_name}': missing runs-on")
        if "steps" not in job or not job["steps"]:
            problems.append(f"job '{job_name}': missing steps")
        else:
            for i, step in enumerate(job["steps"]):
                if not isinstance(step, dict):
                    problems.append(f"job '{job_name}' step {i}: not a mapping")
                    continue
                if "uses" not in step and "run" not in step:
                    problems.append(
                        f"job '{job_name}' step {i} ({step.get('name', '?')}): "
                        "neither 'uses' nor 'run'"
                    )

    # 4. Action pins — org policy requires 40-char SHA
    for m in re.finditer(r"uses:\s*([^\s#]+)", raw):
        ref = m.group(1)
        if "@" not in ref:
            problems.append(f"uses without a ref: {ref}")
        elif not re.search(r"@[0-9a-f]{40}$", ref):
            problems.append(f"not SHA-pinned: {ref}")

    # 5. Hardcoded credentials (a common paste hazard)
    if re.search(r"(?<![\w-])(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36})", raw):
        problems.append("hardcoded credential-looking string in the file")

    # 6. Text that looks like two YAML docs got merged
    if re.search(r"^\s*\S+jobs:\s*$", raw, re.M):
        problems.append("a line reads like 'Xjobs:' — two documents appear concatenated")
    if raw.count("\njobs:") > 1:
        problems.append("more than one top-level 'jobs:' key")

    # 7. Triggers
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        if on not in REQUIRED_ON:
            problems.append(f"unknown trigger: {on}")
    elif isinstance(on, dict):
        pass
    return problems


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = sorted(Path(".").rglob("*.yml"))
    total = 0
    for p in paths:
        problems = check(p)
        if problems:
            total += len(problems)
            print(f"FAIL {p}")
            for pr in problems:
                print(f"     - {pr}")
        else:
            print(f"OK   {p}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
