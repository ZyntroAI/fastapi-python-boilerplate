# GitHub DevOps Toolkit

Standardized, externalized GitHub workflow governance for this repo.

## Contents
- `pr-templates/` — PR templates: feature, bugfix, release, documentation (with YAML front-matter for labels).
- `workflows/` — reference gatekeeper workflows: `pr-checks.yml`, `gitleaks.yml`, `release-drafter.yml` (SHA-pinned).
- `config/` — externalized policy: `settings.json` (branch protection + workflow paths) and `release-drafter.yml`.
- `terraform/` — `main.tf` for branch protection + required status checks via the GitHub provider.

## How to use
1. **PR templates**: copy each `.md` into `.github/PULL_REQUEST_TEMPLATE/`.
2. **Workflows**: copy `.yml` into `.github/workflows/` (requires GitHub App `workflows` permission — org admin).
3. **Branch protection**: apply `terraform/main.tf` (or match `config/settings.json` in the repo UI).
4. **Release Drafter**: place `config/release-drafter.yml` at `.github/release-drafter.yml` and enable the workflow.

All action versions are SHA-pinned to satisfy the org's policy.
