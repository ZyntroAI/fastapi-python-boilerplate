#!/usr/bin/env bash
# promote.sh — move the Full CI/CD pipeline from deliverables/ into .github/workflows/
#
# Dry-run by default. Pass --apply to actually do it.
#
#   ./deliverables/full-cicd-pipeline/promote.sh            # show what would happen
#   ./deliverables/full-cicd-pipeline/promote.sh --apply    # copy + validate + commit
#
# Why this exists: the GitHub App `fig-ai-agent` lacks the `workflows`
# installation scope, so it cannot write to .github/workflows/ itself. This
# script does the promotion from YOUR machine, where that scope does not apply.
#
# Verified 2026-09-14: the three filenames below do NOT collide with anything
# currently in .github/workflows/, so this is a pure add — nothing is removed.
set -euo pipefail

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

SRC="deliverables/full-cicd-pipeline/.github/workflows"
DST=".github/workflows"
FILES=(pipeline.yml reusable-python-ci.yml reusable-security-scan.yml)

say()  { printf '%s\n' "$*"; }
run()  { say "  + $*"; [[ "$APPLY" == "1" ]] && "$@" || true; }

# --- preconditions ---------------------------------------------------------
[[ -d "$SRC" ]] || { say "ERROR: $SRC not found — run from the repo root."; exit 1; }
[[ -d "$DST" ]] || { say "ERROR: $DST not found — run from the repo root."; exit 1; }

say "Promote Full CI/CD pipeline  (apply=$APPLY)"
say ""

# --- collision guard -------------------------------------------------------
say "Checking for filename collisions in $DST ..."
collisions=0
for f in "${FILES[@]}"; do
  if [[ -e "$DST/$f" ]]; then
    say "  COLLISION: $DST/$f already exists"
    collisions=$((collisions + 1))
  else
    say "  clear:     $f"
  fi
done
if [[ "$collisions" -gt 0 ]]; then
  say ""
  say "Refusing to continue — resolve the collisions above first."
  say "A pre-existing file is never overwritten by this script."
  exit 1
fi
say ""

# --- copy ------------------------------------------------------------------
say "Copying ${#FILES[@]} files:"
for f in "${FILES[@]}"; do
  run cp "$SRC/$f" "$DST/$f"
done
say ""

# --- validate (read-only; safe in dry-run) ----------------------------------
say "Validating:"
python3 - <<'PY'
import glob, sys
try:
    import yaml
except ImportError:
    print("  SKIP: PyYAML not installed (pip install pyyaml)")
    sys.exit(0)

bad = 0
targets = [".github/workflows/pipeline.yml",
           ".github/workflows/reusable-python-ci.yml",
           ".github/workflows/reusable-security-scan.yml"]
for p in targets:
    try:
        yaml.safe_load(open(p))
        print(f"  parse OK   {p}")
    except FileNotFoundError:
        print(f"  parse SKIP {p} (not copied yet — dry-run)")
    except Exception as e:
        print(f"  parse FAIL {p}: {str(e).splitlines()[0]}")
        bad += 1

# Every remote `uses:` must be a full 40-char SHA. Local reusable workflows
# (`./.github/workflows/x.yml`) are in-repo and are NOT pinned by design — they
# always resolve to the same commit as the caller, so they are exempt.
import re
unpinned = 0
for p in targets:
    try:
        for line in open(p):
            m = re.search(r"uses:\s*(\S+)", line)
            if not m:
                continue
            ref = m.group(1)
            if ref.startswith("./"):
                continue  # local reusable workflow — correctly unpinned
            if not re.search(r"@[0-9a-f]{40}\b", ref):
                print(f"  UNPINNED   {p}: {ref}")
                unpinned += 1
    except FileNotFoundError:
        pass
print(f"  remote refs unpinned: {unpinned}")
sys.exit(1 if (bad or unpinned) else 0)
PY
say ""

# --- local commit (never pushes) -------------------------------------------
if [[ "$APPLY" == "1" ]]; then
  say "Staging and committing (no push — review, then push yourself):"
  git add "$DST/pipeline.yml" "$DST/reusable-python-ci.yml" "$DST/reusable-security-scan.yml"
  git commit -m "ci: promote the Full CI/CD pipeline into .github/workflows/

Adds the three validated workflows from deliverables/full-cicd-pipeline/ at the
repo root so they actually run. Additive only - no existing workflow changes."
  say ""
  say "Done. Review, then:  git push"
else
  say "Dry-run — nothing was copied or committed. Re-run with --apply."
fi
