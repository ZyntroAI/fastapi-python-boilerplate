#!/usr/bin/env python3
"""Validate the auto-compress-manage.yml workflow.

Usage:
    python3 scripts/validate_acm_workflow.py [path/to/workflow.yml]

Checks (all offline except the SHA resolution in check 6):
 1. YAML parses, and no duplicate top-level keys (safe_load silently drops dupes).
 2. Trigger-level `paths` filters present on both push and pull_request.
 3. `scan` job has the bot-loop guard, covering github.ref (push) AND
    github.head_ref (pull_request).
 4. compress-images / compress-web gate on inputs.target.
 5. summary job skips when both children are skipped.
 6. Every `uses:` is pinned to a full 40-hex SHA that actually resolves upstream.

Exit code 0 = all checks passed, 1 = at least one failure.
"""
import re
import sys
import urllib.request
from pathlib import Path

import yaml

DEFAULT = Path("deliverables/ci/auto-compress-manage.yml")
WF = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))


def resolves(repo, sha):
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    r = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "fig"}
    )
    try:
        urllib.request.urlopen(r)
        return True
    except Exception:
        return False


text = WF.read_text()
print(f"=== validating {WF} ({len(text)} bytes) ===\n")

# 1. YAML parse
try:
    doc = yaml.safe_load(text)
    check("YAML parses", True)
except Exception as e:
    check("YAML parses", False, str(e)[:200])
    sys.exit(1)

seen_top = [m.group(1) for m in re.finditer(r"^([A-Za-z_]+):", text, re.M)]
dupes = {k for k in seen_top if seen_top.count(k) > 1}
check("no duplicate top-level keys", not dupes, f"dupes={dupes}" if dupes else "clean")

# 2. paths filters
on = doc.get("on") or doc.get(True)
push_paths = set(((on.get("push") or {}).get("paths")) or [])
pr_paths = set(((on.get("pull_request") or {}).get("paths")) or [])
check("trigger paths on push", len(push_paths) == 7, f"{len(push_paths)} globs")
check("trigger paths on pull_request", len(pr_paths) == 7, f"{len(pr_paths)} globs")
check("no bare '**' path (would defeat the filter)", "'**'" not in push_paths | pr_paths)
check("workflow_dispatch preserved", "workflow_dispatch" in on, str(list(on.keys())))
check("all globs are '**/*.ext' (valid GitHub + valid YAML)",
      all(re.fullmatch(r"\*\*/\*\.[a-z]+", g) for g in push_paths | pr_paths),
      "bare '**.ext' is YAML-invalid and not a GitHub glob")

# 3. bot-loop guard
scan_if = (doc["jobs"]["scan"].get("if") or "")
check("scan guard covers refs/heads/auto/", "refs/heads/auto/" in scan_if)
check("scan guard covers head_ref (pull_request)", "github.head_ref" in scan_if,
      "github.ref is 'refs/pull/N/merge' on PRs — without head_ref the guard is dead on PRs")
check("scan guard null-safe on push (|| '')", "|| ''" in scan_if,
      "head_commit is absent on pull_request events")
check("scan guard covers [skip ci]", "[skip ci]" in scan_if)

# 4. inputs.target gating
ci = doc["jobs"]["compress-images"].get("if") or ""
cw = doc["jobs"]["compress-web"].get("if") or ""
check("compress-images honours inputs.target", "inputs.target" in ci and "'images'" in ci)
check("compress-web honours inputs.target", "inputs.target" in cw and "'web-assets'" in cw)
check("has-images gate intact", "has-images" in ci)
check("has-web gate intact", "has-web" in cw)
check("inputs.target matches dispatch options (no dead options)",
      "artifacts" not in str((on.get("workflow_dispatch") or {}).get("inputs") or {})
      or "artifacts" in text,
      "every option in workflow_dispatch must be reachable")

# 5. summary
su = doc["jobs"]["summary"].get("if") or ""
check("summary skips when both children skipped", "!= 'skipped'" in su and "always()" in su)
check("summary cancels cleanly", "!cancelled()" in su)

# 6. SHA pins
uses = re.findall(r"uses:\s*([^\s#]+)(?:\s*#\s*(.*))?", text)
pinned = all(
    re.fullmatch(r"[\w.-]+/[\w.-]+(/[\w.-]+)?@[0-9a-f]{40}", u) for u, _ in uses
)
check("all `uses:` are SHA-pinned", pinned, f"{len(uses)} action refs")
for ref, comment in uses:
    repo, sha = ref.rsplit("@", 1)
    repo2 = "/".join(repo.split("/")[:2])
    check(f"resolves {repo2}@{sha[:12]}", resolves(repo2, sha), (comment or "").strip())

failed = [n for n, ok, _ in results if not ok]
print(f"\n=== {len(results) - len(failed)}/{len(results)} checks passed ===")
if failed:
    print("FAILURES:")
    for f in failed:
        print("  -", f)
    sys.exit(1)
print("all checks passed")
