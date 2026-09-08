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

## Official sources

- Docs: `gh help` · <https://cli.github.com/manual>
- Repository: <https://github.com/cli/cli>
