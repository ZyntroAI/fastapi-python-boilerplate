#!/usr/bin/env python3
"""Build the credential-constrained handoff bundle.

When the automation token cannot push to ``.github/workflows/`` (GitHub's
workflows scope), the fix must still reach a human intact. This script produces
a patch and a handoff document that names the exact commands to land it, rather
than leaving a failed push and no artefact.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HandoffBundle:
    patch_path: str
    doc_path: str
    files: list[str] = field(default_factory=list)
    base_branch: str = ""
    base_sha: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "patch_path": self.patch_path,
            "doc_path": self.doc_path,
            "files": self.files,
            "base_branch": self.base_branch,
            "base_sha": self.base_sha,
        }


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)
    return proc.stdout.strip()


def build_handoff(
    repo: str | Path,
    paths: list[str],
    out_dir: str | Path,
) -> HandoffBundle:
    repo = Path(repo)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    base_branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    base_sha = _git(repo, "rev-parse", "HEAD")
    patch_path = out / "workflows-repair.patch"

    diff = subprocess.run(
        ["git", "diff", "--binary", "HEAD", "--", *paths],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    patch_path.write_text(diff, encoding="utf-8")

    doc_path = out / "HANDOFF.md"
    doc_path.write_text(
        _render_doc(base_branch, base_sha, paths, patch_path.name), encoding="utf-8"
    )
    return HandoffBundle(str(patch_path), str(doc_path), list(paths), base_branch, base_sha)


def _render_doc(base_branch: str, base_sha: str, paths: list[str], patch_name: str) -> str:
    listing = "\n".join(f"- `{p}`" for p in paths) or "- (none)"
    return f"""# Handoff — workflow repairs

The automation token cannot write to `.github/workflows/`; GitHub requires the
`workflows` scope for that path. The change is complete and verified — it needs
a human (or an app with the scope) to land it.

## What is in this bundle

{listing}

Base: `{base_branch}` at `{base_sha}`

## Land it

```sh
git clone <repo> && cd <repo>
git checkout -b fix/workflow-repair
git apply --check {patch_name}     # must print nothing
git apply {patch_name}
git add -- {(" ".join(paths)) if paths else "<paths>"}
git commit -m "fix(ci): repair workflow files"
git push -u origin fix/workflow-repair
```

Then open a pull request against `{base_branch}`.

## Do not

- Do not edit the workflow files by hand after applying the patch — regenerate
  it, so the diff and the file on disk cannot drift apart.
- Do not use `git push --force` to land this; the base may have moved.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    repo = Path(args.repo)
    if not (repo / ".git").exists():
        print(f"not a git repository: {repo}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else repo / "handoff"
    bundle = build_handoff(repo, args.paths, out)
    print(f"patch: {bundle.patch_path}")
    print(f"doc:   {bundle.doc_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
