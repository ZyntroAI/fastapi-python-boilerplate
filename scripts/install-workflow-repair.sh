#!/usr/bin/env bash
#
# install-workflow-repair.sh — land the repaired workflow set on
# ZyntroAI/fastapi-python-boilerplate.
#
# WHY THIS EXISTS
#   CI on `main` fails at "Set up job" for every job, before a single test runs.
#   Two causes: six workflow files that do not parse or were never registered,
#   and action refs that violate the repo's own full-SHA pin policy (six of them
#   fabricate near-miss SHAs that look pinned and resolve to nothing).
#
#   The repair already exists ON `main`, under `deliverables/ci/workflows-repaired/`.
#   It cannot be landed by the Fig GitHub App: the App has no `workflows` scope,
#   so a push touching `.github/workflows/**` is refused at the transport layer —
#   before a PR can even be opened. A maintainer (or any actor with the scope)
#   runs this script instead.
#
# USAGE
#   bash install-workflow-repair.sh            # dry-run (default) — prints the plan
#   bash install-workflow-repair.sh --apply    # install, verify, commit, push, open PR
#
# Requires: git, python3 with PyYAML, and `gh` authenticated with a token that
# carries the `workflow` scope.

set -euo pipefail

REPO="ZyntroAI/fastapi-python-boilerplate"
BRANCH="fix/workflow-repair-and-sha-pins"
BASE="main"
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

run() {
    if [ "$APPLY" = "1" ]; then
        "$@"
    else
        printf '  [dry-run] %s\n' "$*"
    fi
}

echo "repo   : $REPO"
echo "branch : $BRANCH -> $BASE"
echo "mode   : $([ "$APPLY" = 1 ] && echo APPLY || echo DRY-RUN)"
echo

WORK="${TMPDIR:-/tmp}/workflow-repair-$$"
run mkdir -p "$WORK"

echo "1. clone $BASE"
run git clone --depth 1 --branch "$BASE" "https://github.com/$REPO.git" "$WORK/repo"
if [ "$APPLY" = "1" ]; then
    cd "$WORK/repo"
fi

echo
echo "2. install the repaired set (script ships on $BASE)"
run bash deliverables/ci/workflows-repaired/install.sh --apply

echo
echo "3. verify with the repo's own gate"
run python3 deliverables/ci/verify_workflows.py --check-shas

echo
echo "4. branch, commit, push"
run git checkout -b "$BRANCH"
run git add .github/
run git -c user.name="fig-ai-agent[bot]" \
        -c user.email="fig-ai-agent@users.noreply.github.com" \
        commit -m "fix(ci): install repaired workflows and SHA-pin every action ref

Six workflow files on main did not parse or were never registered, and 60
action refs violated the repo's full-SHA pin policy -- six of them fabricated
near-miss SHAs that look pinned and resolve to nothing. Every CI job died at
'Set up job' before a test ran.

Installed from deliverables/ci/workflows-repaired/ via install.sh.
Verified: verify_workflows.py --check-shas -> PASS."
run git push -u origin "$BRANCH"

echo
echo "5. open the PR"
run gh pr create --repo "$REPO" --base "$BASE" --head "$BRANCH" \
    --title "fix(ci): install repaired workflows and SHA-pin every action ref" \
    --body "Installs the repaired workflow set already on \`main\` under \`deliverables/ci/workflows-repaired/\`.

**Root cause.** Every job failed at \`Set up job\` in ~2s, before any test ran:
- \`Auto-Index-Sync.yml\` / \`dependabot-automerge.yml\` — unterminated single-quoted \`run:\` block swallowed following lines
- \`secret-scan.yml\` — \`workflow_dispatch;\` should be \`workflow_dispatch:\`
- \`test-suite.yml\` — a prose chat reply wrapped in a code fence; GitHub saw no workflow
- \`github-actions-autodebug-autorerun\` — no \`.yml\` extension, never registered
- \`release_drafter.yaml\` — release-drafter *config*, not a workflow; moved to \`.github/release-drafter.yml\`
- six fabricated near-miss SHAs (\`actions/checkout@f548e57c...\` where v4.4.0 is \`11d5960a...\`)

**Verified.** \`python3 deliverables/ci/verify_workflows.py --check-shas\` → PASS."

echo
if [ "$APPLY" = "1" ]; then
    echo "Done. PR opened against $BASE."
else
    echo "Dry-run complete — nothing was written. Re-run with --apply to execute."
fi
echo "Work dir: $WORK"
