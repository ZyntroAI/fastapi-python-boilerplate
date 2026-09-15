#!/usr/bin/env python3
"""Verify every GitHub Actions workflow in this repo.

Three independent checks, each of which has caught a real defect here:

  1. PARSE   -- does the file load as YAML at all?
  2. SHAPE   -- does it have `on:` and `jobs:`, so GitHub will register it?
  3. PINS    -- is every `uses:` pinned to a full 40-hex SHA that actually
                EXISTS? Shape alone is not enough: this repo had well-formed
                SHAs that GitHub answers 404/422 for, which fails every job at
                `Set up job` while the linter stays green.

Exit code is non-zero if anything fails, so it can gate CI.

    python deliverables/ci/verify_workflows.py
    python deliverables/ci/verify_workflows.py --check-shas   # slower, network
"""
from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*['\"]?([^'\"\s#]+)", re.M)
SHA_RE = re.compile(r"[0-9a-f]{40}")

# git must talk to github.com directly: the Fig gitconfig rewrites github.com to
# an enterprise host that cannot serve public third-party repos.
LS_ENV = {
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "PATH": "/usr/bin:/bin:/usr/local/bin",
    "HOME": "/tmp",
}

# repo -> full ref listing (cached: one network call per distinct action repo)
_REF_CACHE: dict[str, str] = {}


def repo_of(action: str) -> str:
    """github/codeql-action/init -> github/codeql-action"""
    return "/".join(action.split("/")[:2])


def real_sha(action: str, sha: str) -> bool:
    """True if `sha` names a commit/branch/tag in the action's repository.

    Two pitfalls, both of which silently produce false "does not exist":

    1. `git ls-remote <url> <sha>` is NOT a membership test -- ls-remote takes
       ref *patterns*, so a raw SHA matches nothing and every pin looks fake.
       List the remote's refs once and test membership instead.
    2. Do NOT pass `--refs`. It suppresses the peeled `<tag>^{}` lines, and for
       an annotated tag the peeled line is the only place the *commit* hash
       appears -- so an annotated-tag pin would be reported as fake. Without
       `--refs` both lightweight (commit straight) and annotated (peeled) tags
       resolve, while a fabricated SHA still matches nothing.
    """
    repo = repo_of(action)
    if repo not in _REF_CACHE:
        r = subprocess.run(
            ["git", "ls-remote", "--tags", "--heads",
             f"https://github.com/{repo}"],
            capture_output=True, text=True, env=LS_ENV,
        )
        _REF_CACHE[repo] = r.stdout
    return sha in _REF_CACHE[repo]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows", default=".github/workflows")
    ap.add_argument("--check-shas", action="store_true",
                    help="confirm each SHA exists (one network call per action repo)")
    args = ap.parse_args()

    files = sorted(f for f in glob.glob(f"{args.workflows}/*") if Path(f).is_file())
    if not files:
        print(f"no workflow files under {args.workflows}")
        return 1

    failures = []
    all_refs: dict[tuple[str, str], list[str]] = {}

    for f in files:
        name = Path(f).name
        raw = Path(f).read_text(encoding="utf-8", errors="replace")

        try:
            doc = yaml.safe_load(raw)
        except Exception as exc:
            mark = getattr(exc, "problem_mark", None)
            where = f" line {mark.line + 1}" if mark else ""
            failures.append(f"{name}: YAML does not parse ({type(exc).__name__}{where})")
            continue

        if not isinstance(doc, dict) or "jobs" not in doc:
            failures.append(f"{name}: no `jobs:` key -- GitHub will not register it")
            continue
        # YAML 1.1 reads a bare `on:` as the boolean True
        if not (doc.get("on") or doc.get(True)):
            failures.append(f"{name}: no `on:` trigger")

        for ref in USES_RE.findall(raw):
            if ref.startswith("./"):
                continue
            action, _, ref_sha = ref.rpartition("@")
            if not SHA_RE.fullmatch(ref_sha):
                failures.append(f"{name}: {ref} is not pinned to a 40-hex SHA")
                continue
            all_refs.setdefault((action, ref_sha), []).append(name)

    if args.check_shas:
        print(f"resolving {len(all_refs)} unique action refs "
              f"({len({repo_of(a) for a, _ in all_refs})} repositories) ...")
        for (action, sha) in sorted(all_refs):
            if not real_sha(action, sha):
                failures.append(
                    f"{action}@{sha[:12]} is well-formed but does not exist "
                    f"(used in {', '.join(sorted(set(all_refs[(action, sha)])))})"
                )

    if failures:
        print(f"FAIL — {len(failures)} problem(s) across {len(files)} workflows:\n")
        for x in failures:
            print(f"  - {x}")
        return 1

    print(f"PASS — {len(files)} workflows parse, are shaped correctly, "
          f"and all {len(all_refs)} action refs are SHA-pinned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
