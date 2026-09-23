"""Build the workflow repair set for ZyntroAI/fastapi-python-boilerplate.

Pipeline, in order:
  1. extract  the two markdown-wrapped files into real workflow YAML
  2. repair   YAML damage (stray `;`, unindented block scalar, appended docs)
  3. pin      every `uses:` to a full-length commit SHA
  4. validate every file parses and every ref is a 40-hex SHA
  5. emit     a git patch against the repo root, plus the fixed files, into
              deliverables/workflow-repair/ (a nested path — the root
              .github/workflows/ is push-blocked for this App)

Nothing is written into .github/workflows/ in the final PR.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HOME = "/workspace/H7tGkmt5NUfW1dxEb7zSB64VDoY2/7aa25c80-ed0f-4616-a14d-0531cab130f7"
REPO = os.path.join(HOME, "raw_data", "fpsb")
SCRIPTS = os.path.join(HOME, "scripts")
OUT = os.path.join(REPO, "deliverables", "workflow-repair")
WFDIR = os.path.join(REPO, ".github", "workflows")

sys.path.insert(0, SCRIPTS)
import yaml  # noqa: E402
from repair_workflows import repair_yaml, parses  # noqa: E402
from extract_wrapped_workflows import fenced_yaml, from_first_key  # noqa: E402
from fix_workflow_pins import PINS, USES_RE, action_name  # noqa: E402


def sh(cmd, cwd=REPO, check=True):
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if check and p.returncode != 0:
        print("CMD FAILED:", cmd, "\n", p.stderr[:400])
    return p.stdout


def pin_text(text):
    """Pin every uses: line; return (new_text, edits, unresolved)."""
    edits, unresolved, out = [], [], []
    for i, line in enumerate(text.split("\n"), 1):
        m = USES_RE.match(line)
        if not m:
            out.append(line)
            continue
        spec = m.group("spec")
        if spec.startswith("./") or "${{" in spec:
            out.append(line)
            continue
        name = action_name(spec)
        ref = spec.rsplit("@", 1)[1] if "@" in spec else ""
        pin = PINS.get(name)
        if pin is None:
            unresolved.append(f"{name}@{ref}")
            out.append(line)
            continue
        sha, tag = pin
        if ref != sha:
            edits.append(f"{spec} -> @{sha[:12]}…")
        subpath = spec.split("@", 1)[0].split("/")[2:]
        base = name + ("/" + "/".join(subpath) if subpath else "")
        out.append(f"{m.group('indent')}uses: {base}@{sha}  # {tag}")
    return "\n".join(out), edits, unresolved


def main():
    # --- 0. clean slate: make sure workflows are pristine before we start
    sh("git checkout -- .github/workflows")

    report = {"extracted": [], "yaml_fixed": [], "pins": {},
              "unresolved": {}, "files": {}}

    # --- 1. extract the markdown-wrapped files
    #   test-suite.yml                        -> itself (body of the ```yaml fence)
    #   github-actions-autodebug-autorerun    -> auto-debug-rerun.yml (starts at first `name:`)
    ts = os.path.join(WFDIR, "test-suite.yml")
    body, span = fenced_yaml(open(ts, encoding="utf-8").read())
    assert body, "could not extract test-suite.yml fence"
    open(ts, "w", encoding="utf-8", newline="\n").write(body)
    report["extracted"].append(f"test-suite.yml <- ```yaml fence, lines {span[0]}-{span[1]}")

    au = os.path.join(WFDIR, "github-actions-autodebug-autorerun")
    body2, span2 = from_first_key(open(au, encoding="utf-8").read())
    assert body2, "could not extract autodebug spec"
    os.remove(au)                                   # not a workflow: no .yml extension
    open(os.path.join(WFDIR, "auto-debug-rerun.yml"), "w",
         encoding="utf-8", newline="\n").write(body2)
    report["extracted"].append(
        f"auto-debug-rerun.yml <- github-actions-autodebug-autorerun, lines {span2[0]}-{span2[1]} "
        f"(source file had no .yml extension, so GitHub never loaded it)")

    # --- 2 + 3. repair YAML, then pin
    for fn in sorted(os.listdir(WFDIR)):
        path = os.path.join(WFDIR, fn)
        if not os.path.isfile(path):
            continue
        raw = open(path, encoding="utf-8", newline="").read()

        text, notes = repair_yaml(path, raw)
        for n in notes:
            report["yaml_fixed"].append(f"{fn}: {n}")

        text, edits, unresolved = pin_text(text)
        if edits:
            report["pins"][fn] = edits
        if unresolved:
            report["unresolved"][fn] = unresolved

        ok, why = parses(text)
        report["files"][fn] = {"parses": ok, "why": why, "lines": len(text.split("\n"))}
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    # --- 4. validate everything
    print("=== validation ===")
    all_ok = True
    for fn, st in sorted(report["files"].items()):
        flag = "OK " if st["parses"] else "BAD"
        if not st["parses"]:
            all_ok = False
        print(f"  {flag} {fn:<42} {st['lines']:>4} lines  {'' if st['parses'] else st['why']}")
    print(f"  all workflows parse: {all_ok}")

    # every uses: must now be a 40-hex SHA
    bad_refs = sh(r"grep -rho 'uses: [^ ]*@[^ ]*' .github/workflows/ | grep -vE '@[0-9a-f]{40}'")
    print(f"  non-pinned refs remaining: {len([l for l in bad_refs.splitlines() if l.strip()])}")
    if bad_refs.strip():
        print("   ", bad_refs.strip()[:300])

    # --- 5. emit the patch + a copy of the fixed tree
    # untracked files (the renamed auto-debug-rerun.yml) do not show up in
    # `git diff` — stage first so the patch carries both the deletion of the
    # extensionless file and the addition of its replacement.
    sh("git add -A -- .github/workflows")
    patch = sh("git diff --cached -- .github/workflows")
    sh("git reset -q -- .github/workflows")
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, ".github", "workflows"), exist_ok=True)
    for fn in sorted(os.listdir(WFDIR)):
        p = os.path.join(WFDIR, fn)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(OUT, ".github", "workflows", fn))
    open(os.path.join(OUT, "workflow-repair.patch"), "w", encoding="utf-8").write(patch)
    json.dump(report, open(os.path.join(OUT, "repair-report.json"), "w"), indent=2)

    sh("git reset -q -- .github/workflows")
    sh("git checkout -- .github/workflows")          # PR must not touch root workflows
    sh("git clean -fd -- .github/workflows")

    print("\n=== report ===")
    for e in report["extracted"]:
        print("  extract: " + e)
    for e in report["yaml_fixed"]:
        print("  yaml:    " + e)
    print(f"  pinned files: {len(report['pins'])}  total ref edits: {sum(len(v) for v in report['pins'].values())}")
    for f, u in report["unresolved"].items():
        print(f"  UNRESOLVED {f}: {u}")
    print(f"\n  patch bytes: {len(patch)}")
    print(f"  output: {OUT}")


if __name__ == "__main__":
    main()
