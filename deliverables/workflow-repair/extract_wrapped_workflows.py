"""Extract the real workflow YAML out of two markdown-wrapped files.

  test-suite.yml                          -> body inside a ```yaml fence
  github-actions-autodebug-autorerun      -> prose spec; YAML starts at the
                                             first top-level `name:` key

Writes the extracted YAML to a target path. Dry run by default.
"""
import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required")


def fenced_yaml(text):
    """Return the body of the first ```yaml ... ``` fence, or None."""
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^```ya?ml\s*$", ln, re.I):
            start = i + 1
            break
    if start is None:
        return None, None
    for j in range(start, len(lines)):
        if lines[j].startswith("```"):
            return "\n".join(lines[start:j]).rstrip("\n") + "\n", (start + 1, j)
    return None, None


def from_first_key(text):
    """Return the largest valid YAML prefix starting at the first `name:`."""
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^name:\s", ln):
            start = i
            break
    if start is None:
        return None, None
    for end in range(len(lines), start, -1):
        cand = "\n".join(lines[start:end]).rstrip("\n") + "\n"
        try:
            d = yaml.safe_load(cand)
        except yaml.YAMLError:
            continue
        if isinstance(d, dict) and "jobs" in d:
            return cand, (start + 1, end)
    return None, None


TARGETS = {
    "test-suite.yml": ("fenced", None),
    "github-actions-autodebug-autorerun": ("firstkey", "auto-debug-rerun.yml"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out-dir", default=None,
                    help="where to write extracted files (default: alongside, in the workflows dir)")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    wf = os.path.join(args.repo, ".github", "workflows")
    out_dir = args.out_dir or wf

    for fn, (mode, newname) in TARGETS.items():
        src = os.path.join(wf, fn)
        if not os.path.isfile(src):
            print(f"skip {fn} (absent)")
            continue
        text = open(src, encoding="utf-8").read()
        body, span = (fenced_yaml(text) if mode == "fenced" else from_first_key(text))
        if not body:
            print(f"FAIL {fn}: could not extract")
            continue
        # validate the extraction
        try:
            docs = [d for d in yaml.safe_load_all(body) if d is not None]
        except yaml.YAMLError as e:
            print(f"FAIL {fn}: extracted body does not parse: {e}")
            continue
        if len(docs) != 1 or not isinstance(docs[0], dict) or "jobs" not in docs[0]:
            print(f"FAIL {fn}: extracted body is not a single workflow mapping")
            continue
        dest_name = newname or fn
        dest = os.path.join(out_dir, dest_name)
        print(f"OK   {fn}  lines {span[0]}-{span[1]}  ->  {dest_name} "
              f"({len(body.splitlines())} lines, {len(docs[0]['jobs'])} jobs)")
        if args.apply:
            with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
            print(f"     wrote {dest}")


if __name__ == "__main__":
    main()
