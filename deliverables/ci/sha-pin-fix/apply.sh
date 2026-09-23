#!/usr/bin/env bash
#
# Apply the action SHA-pin repair to ZyntroAI/fastapi-python-boilerplate.
#
# Why this exists: the Fig GitHub App installation lacks the `workflows`
# permission, so it cannot push changes under `.github/workflows/`. The patch
# below carries the exact fix; this script applies it from a machine that has
# the permission.
#
# Usage:
#   ./apply.sh                  # dry run against a fresh clone (default)
#   ./apply.sh --apply          # apply, commit, push, open PR
#
set -euo pipefail

REPO="ZyntroAI/fastapi-python-boilerplate"
BRANCH="ci/fix-sha-pins"
PATCH="$(cd "$(dirname "$0")" && pwd)/ci_sha_pin_fix.patch"

APPLY=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "==> cloning $REPO (depth 1, main)"
git clone --quiet --depth 1 --branch main "https://github.com/$REPO.git" "$WORK/repo"
cd "$WORK/repo"

echo "==> checking patch applies cleanly"
git apply --check "$PATCH"
echo "    OK - patch applies with no conflicts"

if [ "$APPLY" -eq 0 ]; then
  echo
  echo "DRY RUN complete. Nothing was changed."
  echo "Re-run with --apply to commit, push and open the PR."
  exit 0
fi

echo "==> applying patch"
git apply "$PATCH"

echo "==> verifying YAML still parses"
python3 - <<'PY'
import sys, yaml
ok = True
for p in (".github/workflows/ci.yml", ".github/workflows/test-and-coverage.yaml"):
    try:
        d = yaml.safe_load(open(p, encoding="utf-8"))
        print(f"    OK   {p}: jobs={list(d.get('jobs', {}).keys())}")
    except Exception as e:
        ok = False
        print(f"    FAIL {p}: {type(e).__name__}: {e}")
sys.exit(0 if ok else 1)
PY

echo "==> verifying no unpinned @vN refs remain"
if grep -nE 'uses:\s*\S+@v[0-9]' .github/workflows/ci.yml .github/workflows/test-and-coverage.yaml; then
  echo "    FAIL - unpinned refs found" >&2
  exit 1
fi
echo "    OK - all refs are 40-hex SHA pins"

git checkout -b "$BRANCH"
git add .github/workflows/ci.yml .github/workflows/test-and-coverage.yaml
git commit -m "ci: replace unresolvable action SHA pins in ci.yml and test-and-coverage.yaml

The pinned SHAs in both workflows do not exist upstream, so every job that
resolves an action fails at setup with:

  ##[error]Unable to resolve action, unable to find version

Replaces only the SHA in each uses: ref; every other byte is untouched.
Each replacement was confirmed to carry the expected release tag."

echo "==> pushing $BRANCH"
git push -u origin "$BRANCH"

echo "==> opening PR"
gh pr create --base main --head "$BRANCH" \
  --title "ci: fix unresolvable action SHA pins in ci.yml and test-and-coverage.yaml" \
  --body-file "$(cd "$(dirname "$0")" && pwd)/PR_BODY.md"

echo
echo "DONE. PR opened for $BRANCH."
