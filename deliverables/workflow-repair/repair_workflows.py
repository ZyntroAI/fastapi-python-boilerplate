"""Repair ZyntroAI/fastapi-python-boilerplate's GitHub workflows.

Two independent defect classes both break CI at the `Set up job` step:

  A. YAML damage — four files are not parseable YAML at all:
       secret-scan.yml            stray `;` where a `:` belongs
       Auto-Index-Sync.yml        unindented block scalar (embedded python at col 0)
       dependabot-automerge.yml   ~85 lines of GitHub docs appended after the workflow
       test-suite.yml             appended markdown starting at a ``` fence
  B. Unpinned action refs — 72 `uses:` lines using floating tags, literal
     `<commit-sha>` placeholders, or SHAs that do not exist upstream.

Usage:
    python3 repair_workflows.py <repo_dir>          # dry run (default)
    python3 repair_workflows.py <repo_dir> --apply  # write changes

Every write is followed by a YAML parse of the result; nothing is written that
does not parse.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_workflow_pins import PINS, USES_RE, action_name, BAD_SHA_NOTE  # noqa: E402

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required:  pip install pyyaml")


# ---------------------------------------------------------------- YAML repairs

STRAY_SEMICOLON = [
    ("  workflow_dispatch;", "  workflow_dispatch:"),
]

# the placeholder script is emitted as a multi-line single-quoted string whose
# continuation lines sit at column 0, which terminates the `run: |` block scalar.
OLD_PLACEHOLDER = """            echo '#!/usr/bin/env python3
import sys
print("# Policy Snapshot\\n")
print("Source:", sys.argv[1])
' > scripts/parse_docs.py"""

NEW_PLACEHOLDER = """            echo '#!/usr/bin/env python3' > scripts/parse_docs.py
            echo 'import sys' >> scripts/parse_docs.py
            printf 'print("# Policy Snapshot\\\\n")\\n' >> scripts/parse_docs.py
            echo 'print("Source:", sys.argv[1])' >> scripts/parse_docs.py"""

# file -> regex marking the first line of appended documentation
TRUNCATE_AT = {
    "dependabot-automerge.yml": r"^# Navigating code on GitHub",
    "test-suite.yml": r"^```\s*$",
}


def repair_yaml(path, text):
    """Return (new_text, [notes]). Never raises."""
    notes = []
    fn = os.path.basename(path)

    for old, new in STRAY_SEMICOLON:
        if old in text:
            text = text.replace(old, new, 1)
            notes.append(f"fixed stray semicolon: {old.strip()!r} -> {new.strip()!r}")

    if OLD_PLACEHOLDER in text:
        text = text.replace(OLD_PLACEHOLDER, NEW_PLACEHOLDER, 1)
        notes.append("re-indented embedded python placeholder into the run block")

    pat = TRUNCATE_AT.get(fn)
    if pat:
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if re.match(pat, ln):
                dropped = len(lines) - i
                text = "\n".join(lines[:i]).rstrip("\n") + "\n"
                notes.append(f"truncated {dropped} lines of appended documentation at line {i+1}")
                break

    return text, notes


def parses(text):
    try:
        docs = list(yaml.safe_load_all(text))
    except yaml.YAMLError as e:
        return False, f"{e.problem} (line {getattr(e.problem_mark, 'line', -1) + 1})"
    live = [d for d in docs if d is not None]
    if len(live) > 1:
        return False, f"{len(live)} YAML documents in one workflow file"
    if not isinstance(live[0] if live else None, dict):
        return False, "top level is not a mapping"
    return True, "ok"


# ---------------------------------------------------------------------- driver

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    wf_dir = os.path.join(args.repo, ".github", "workflows")
    if not os.path.isdir(wf_dir):
        sys.exit(f"no workflows dir at {wf_dir}")

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== {mode} — {os.path.abspath(args.repo)} ===\n")

    yaml_fixed, pin_edits, unresolved, reverted = [], [], [], []

    for fn in sorted(os.listdir(wf_dir)):
        path = os.path.join(wf_dir, fn)
        if not os.path.isfile(path):
            continue

        with open(path, encoding="utf-8", newline="") as fh:
            original = fh.read()
        nl = "\r\n" if "\r\n" in original else "\n"
        text = original

        before_ok, before_why = parses(text)

        # --- stage A: YAML repair
        text, notes = repair_yaml(path, text)
        for n in notes:
            yaml_fixed.append(f"{fn}: {n}")

        # --- stage B: pin action refs
        out_lines = []
        for i, line in enumerate(text.split("\n"), 1):
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
                unresolved.append(f"{fn}:{i}  {spec}")
                out_lines.append(line)
                continue
            sha, tag = pin
            if ref != sha:
                why = ("placeholder" if ("<" in ref or ">" in ref) else
                       "non-existent SHA" if ref in BAD_SHA_NOTE else
                       "invalid tag" if re.fullmatch(r"[A-Za-z0-9._-]+", ref) and not re.fullmatch(r"[0-9a-f]{40}", ref) else
                       "wrong SHA")
                pin_edits.append(f"{fn}:{i}  {spec}  ->  @{sha[:12]}… ({why})")
            subpath = spec.split("@", 1)[0].split("/")[2:]
            base = name + ("/" + "/".join(subpath) if subpath else "")
            out_lines.append(f"{m.group('indent')}uses: {base}@{sha}  # {tag}")
        text = "\n".join(out_lines)

        # --- validate
        after_ok, after_why = parses(text)
        if not after_ok:
            reverted.append(f"{fn}: STILL INVALID -> {after_why}")
            if args.apply:
                print(f"  !! {fn}: repair did not parse, leaving file untouched ({after_why})")
            continue

        if text != original:
            if before_ok:
                print(f"  pin-only    {fn}")
            else:
                print(f"  yaml+pin    {fn}   (was: {before_why})")
            if args.apply:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(text)
        else:
            status = "ok" if before_ok else f"BROKEN ({before_why})"
            print(f"  unchanged   {fn}   [{status}]")

    print("\n--- YAML repairs ---")
    for n in yaml_fixed:
        print("  " + n)
    print(f"--- action ref pins: {len(pin_edits)} ---")
    for n in pin_edits[:8]:
        print("  " + n)
    if len(pin_edits) > 8:
        print(f"  ... and {len(pin_edits) - 8} more")
    if unresolved:
        print("--- unresolved (needs a human) ---")
        for n in unresolved:
            print("  " + n)
    if reverted:
        print("--- NOT repairable automatically ---")
        for n in reverted:
            print("  " + n)

    print(f"\nsummary: yaml_fixes={len(yaml_fixed)}  pins={len(pin_edits)}  "
          f"unresolved={len(unresolved)}  unrepairable={len(reverted)}")


if __name__ == "__main__":
    main()
