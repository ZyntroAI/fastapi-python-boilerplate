"""Pin every `uses:` in a GitHub repo's workflows to a full-length commit SHA.

Repairs three distinct defects, each of which breaks CI at the `Set up job`
step before any code runs:

  1. literal placeholders          actions/checkout@<commit-sha>
  2. non-existent SHAs (fabricated) actions/checkout@f548e57c...   (404 upstream)
  3. invalid tag refs               actions/checkout@v7            (no such tag)
  4. floating major tags            actions/checkout@v4            (policy violation)

Usage:
    python3 fix_workflow_pins.py <repo_dir> [--apply]

Without --apply it is a dry run: it reports what it would change and writes
nothing. With --apply it rewrites the workflow files in place.
"""
import argparse
import json
import os
import re
import subprocess
import sys

# action name -> (full SHA, tag it corresponds to)
PINS = {
    "actions/checkout": ("11d5960a326750d5838078e36cf38b85af677262", "v4"),
    "actions/setup-python": ("a26af69be951a213d495a4c3e4e4022e16d87065", "v5"),
    "actions/upload-artifact": ("ea165f8d65b6e75b540449e92b4886f43607fa02", "v4"),
    "actions/download-artifact": ("d3f86a106a0bac45b974a628896c90dbdf5c8093", "v4"),
    "actions/github-script": ("f28e40c7f34bde8b3046d885e986cb6290c5673b", "v7"),
    "actions/configure-pages": ("983d7736d9b0ae728b81ab479565c72886d7745b", "v5"),
    "actions/deploy-pages": ("368f82528645a54fb793d4d04e342629a3f51346", "v5"),
    "actions/upload-pages-artifact": ("56afc609e74202658d3ffba0e8f6dda462b719fa", "v3"),
    "actions/setup-java": ("cf277c60eb25467037889841efdb72551f06f6c3", "v4"),
    "codecov/codecov-action": ("b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238", "v4"),
    "github/codeql-action": ("3ea06614dafe36dec890db3446326e0d40ce53d4", "v3"),
    "docker/login-action": ("c94ce9fb468520275223c153574b00df6fe4bcc9", "v3"),
    "docker/build-push-action": ("10e90e3645eae34f1e60eeb005ba3a3d33f178e8", "v6"),
    "gitleaks/gitleaks-action": ("ff98106e4c7b2bc287b24eaf42907196329070c7", "v2"),
    "dependabot/fetch-metadata": ("21025c705c08248db411dc16f3619e6b5f9ea21a", "v2"),
    "pascalgn/automerge-action": ("7961b8b5eec56cc088c140b56d864285eabd3f67", "v0.16.4"),
    "softprops/action-gh-release": ("3bb12739c298aeb8a4eeaf626c5b8d85266b0e65", "v2"),
    "subosito/flutter-action": ("1a449444c387b1966244ae4d4f8c696479add0b2", "v2"),
    "somaz94/compress-decompress": ("4aa7a81b5e2c20ac4a865d937466f3d8928f487c", "v1"),
    "r0adkll/sign-android-release": ("349ebdef58775b1e0d8099458af0816dc79b6407", "v1"),
    "apple-actions/import-codesign-certs": ("63fff01cd422d4b7b855d40ca1e9d34d2de9427d", "v3"),
    "apple-actions/download-provisioning-profiles": ("3167792207a5b26099bc0ca22b5010a323dd2a0b", "v1"),
    "apple-actions/upload-testflight-build": ("54dc215b4cd5529730db39f11c84efdb71414e07", "v1"),
    "wzieba/Firebase-Distribution-Github-Action": ("bd494989dd4bec0343f78adee87fe66e48279ad6", "v1"),
}

# refs known to be fabricated / non-existent upstream. Kept explicit so the
# fixer can name them in its report instead of silently swapping them.
BAD_SHA_NOTE = {
    "f548e57c3d3c42e288026812cd22362661c4e8d4": "actions/checkout@f548e57c — 404 upstream",
    "5fda3b9c709277f8cf4290f3a0094ab7e95c1338": "actions/setup-python@5fda3b9c — 404 upstream",
    "11bd71901bbe5b1630ceea73d275971dd864cf32": "actions/checkout@11bd7190 — 404 upstream",
    "eaaf46c7cd7896392741f9d0acf77d8b12592391": "codecov/codecov-action@eaaf46c7 — 404 upstream",
    "4a13b6b08c6420d408f900f841204c8c413bdd32": "docker/build-push-action@4a13b6b0 — 404 upstream",
    "74a5d146c4c96f6db1f1a614812d3d27e93654e7": "docker/login-action@74a5d146 — 404 upstream",
    "977e6ce40888f41234c9b3252437dcf2331daaa2": "github/codeql-action@977e6ce4 — 404 upstream",
}

USES_RE = re.compile(r"^(?P<indent>\s*(?:-\s*)?)uses:\s*(?P<spec>[^\s#]+)(?P<trail>.*)$")


def action_name(spec):
    """'github/codeql-action/analyze@x' -> 'github/codeql-action'."""
    name = spec.split("@", 1)[0]
    parts = name.split("/")
    return "/".join(parts[:2])


def fix_file(path, apply_changes):
    changes, problems = [], []
    out_lines = []
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()

    # preserve the file's own newline convention
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)

    for i, line in enumerate(lines, 1):
        m = USES_RE.match(line)
        if not m:
            out_lines.append(line)
            continue
        spec = m.group("spec")
        if spec.startswith("./") or "${{" in spec:
            out_lines.append(line)
            continue
        name = action_name(spec)
        ref = spec.rsplit("@", 1)[1] if "@" in spec else ""

        pin = PINS.get(name)
        if pin is None:
            problems.append(f"{path}:{i}  {spec}  (no pin known — needs a human)")
            out_lines.append(line)
            continue

        sha, tag = pin
        already_ok = ref == sha
        if not already_ok:
            reason = "floating tag"
            if "<" in ref or ">" in ref:
                reason = "PLACEHOLDER ref"
            elif ref in BAD_SHA_NOTE:
                reason = "NON-EXISTENT SHA"
            elif re.fullmatch(r"[0-9a-f]{40}", ref):
                reason = "wrong SHA"
            changes.append(f"{path}:{i}  {spec}  ->  @{sha[:12]}…  ({reason}; was {ref})")

        # keep a human-readable version comment, replacing any stale one
        new_line = f"{m.group('indent')}uses: {name}@{sha}  # {tag}"
        # preserve a subpath such as github/codeql-action/init
        subpath = spec.split("@", 1)[0].split("/")[2:]
        if subpath:
            new_line = f"{m.group('indent')}uses: {name}/{'/'.join(subpath)}@{sha}  # {tag}"
        out_lines.append(new_line)

    new_raw = nl.join(out_lines)
    if apply_changes and new_raw != raw:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_raw)
    return changes, problems, (new_raw != raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    wf_dir = os.path.join(args.repo, ".github", "workflows")
    if not os.path.isdir(wf_dir):
        sys.exit(f"no workflows dir at {wf_dir}")

    all_changes, all_problems, touched = [], [], []
    for fn in sorted(os.listdir(wf_dir)):
        p = os.path.join(wf_dir, fn)
        if not os.path.isfile(p):
            continue
        ch, pr, changed = fix_file(p, args.apply)
        all_changes += ch
        all_problems += pr
        if changed:
            touched.append(fn)

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== {mode} — {args.repo} ===")
    for c in all_changes:
        print("  would fix / fixed: " + c)
    for p in all_problems:
        print("  NEEDS HUMAN:       " + p)
    print(f"\nfiles with changes: {len(touched)}")
    for t in touched:
        print("  - " + t)
    print(f"total ref edits: {len(all_changes)}   unresolved: {len(all_problems)}")


if __name__ == "__main__":
    main()
