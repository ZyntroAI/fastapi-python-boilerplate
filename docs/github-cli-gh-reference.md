Title: GitHub CLI (gh) — Complete Reference
Kicker: Official, cross-platform GitHub CLI — replace the web UI with the terminal
Theme: dark
Genre: sop

# GitHub CLI (gh) — Complete Reference

Official, cross-platform (Windows / macOS / Linux) GitHub CLI. It exposes the full GitHub API in your terminal: auth, PRs, issues, workflows, repos, gists, releases, codespaces, and more.

## Install

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux (Debian/Ubuntu)
sudo apt install gh

# Verify
gh --version
```

## Authentication (core)

```bash
# Interactive login (GitHub.com / Enterprise)
gh auth login

# Auth with a token
gh auth login --with-token < token.txt

# Check status / scopes / host / user
gh auth status

# Switch / logout
gh auth switch --user NAME
gh auth logout --hostname github.com

# Auto-configure git credentials
gh auth setup-git
```

## Repository management

```bash
# Create local + remote
gh repo create NAME --public --description "..."

# Clone
gh repo clone OWNER/REPO

# View / browse
gh repo view --web
gh repo list OWNER --limit 20

# Fork / sync
gh repo fork --remote
gh repo sync
```

## Issues & pull requests

```bash
# Issues
gh issue list --assignee @me
gh issue create --title "..." --body "..."
gh issue close ID

# Pull requests
gh pr list --status open
gh pr create --base main --head feature/xyz
gh pr checkout ID
gh pr merge ID --squash
gh pr review ID --approve -b "LGTM"
```

## GitHub Actions / CI-CD

```bash
# Workflows
gh workflow list
gh workflow run FILE.yml --ref main
gh run watch ID
gh run log ID

# Secrets / variables
gh secret list
gh secret set NAME
gh secret delete NAME
gh variable list
gh variable set NAME --env prod
gh env list
```

## Releases, gists, codespaces

```bash
gh release create v1.0.0 --draft
gh gist create FILE --public
gh codespace create
gh codespace code
gh codespace ssh
```

## Extensions & output

```bash
# Install extensions
gh extension install github/gh-copilot

# JSON / table output
gh pr list --json number,title --template TPL
```

## Quick reference sheet

Pattern: `gh <resource> <action> [flags]`

- **Auth** — `gh auth login / status`
- **Repo** — `gh repo create / clone / view`
- **Issue** — `gh issue list / create / close`
- **PR** — `gh pr list / create / merge / review`
- **Actions** — `gh workflow list / run`, `gh run log`
- **Secrets** — `gh secret / variable`

## DevOps pipeline example (gh-driven release)

A complete release/deploy flow driven entirely by `gh`, mirroring a typical
PR → CI → merge → tag → release pipeline. Save as e.g. `scripts/release.sh`.

```bash
#!/usr/bin/env bash
# Usage: ./release.sh OWNER/REPO v1.2.0 "Release title"
set -euo pipefail

REPO="${1:?owner/repo}"; VERSION="${2:?version}"; TITLE="${3:?title}"

echo "→ Opening draft PR for CI to run on…"
# Create a PR (from an existing feature branch) so checks kick off
PR_URL=$(gh pr create --repo "$REPO" --base main --head feature/x \
  --title "chore(release): $TITLE" --body "Automated release pipeline")
PR=$(echo "$PR_URL" | sed 's|.*/pull/||')

echo "→ Waiting for required checks on PR #$PR…"
# Poll until all checks pass (timeout after ~10 min)
for _ in $(seq 1 60); do
  STATE=$(gh pr checks "$PR" --repo "$REPO" --watch --interval 10 2>/dev/null | grep -qE "pass|success" && echo pass || echo pending)
  [ "$STATE" = pass ] && break
  sleep 10
done

echo "→ Merging PR #$PR (squash)…"
gh pr merge "$PR" --repo "$REPO" --squash --delete-branch

echo "→ Tagging and cutting the release…"
git fetch --quiet origin main
git tag "$VERSION" origin/main
git push origin "$VERSION"
gh release create "$VERSION" --repo "$REPO" --title "$TITLE" \
  --notes "See the changelog for $VERSION." dist/*.zip 2>/dev/null || \
gh release create "$VERSION" --repo "$REPO" --title "$TITLE" \
  --notes "See the changelog for $VERSION."

echo "→ Watching deploy workflow (if triggered on release)…"
gh run list --repo "$REPO" --workflow deploy.yml --limit 1
gh run watch --repo "$REPO" "$(gh run list --repo "$REPO" --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

**Key pipeline primitives used**

| Step | `gh` command |
|---|---|
| Open a PR to trigger CI | `gh pr create` |
| Wait for checks to pass | `gh pr checks <num> --watch` |
| Merge on green | `gh pr merge <num> --squash --delete-branch` |
| Tag the merged commit | `git tag` + `git push origin <tag>` |
| Draft/publish a release | `gh release create <tag> --notes "..."` |
| Watch the deploy job | `gh run list` + `gh run watch` |

## Official sources

- Docs: `gh help` · <https://cli.github.com/manual>
- Repository: <https://github.com/cli/cli>
