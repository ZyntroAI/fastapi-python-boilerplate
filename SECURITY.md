# Security Policy

ZyntroAI treats security vulnerabilities seriously. This document covers which
versions are supported and how to report a vulnerability privately.

## Supported Versions

Only the current release line receives security patches. Older lines are
supported on a best-effort basis.

| Version          | Supported          |
| ---------------- | ------------------ |
| latest (main)    | :white_check_mark: |
| < latest         | :x:                |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security problems.**

Instead, report privately so the issue can be assessed and patched before it
is disclosed:

- **Preferred:** Open a [private security advisory][advisories] on GitHub.
- **Fallback:** Email the maintainer directly if you cannot use the advisory
  flow. (Link the relevant repository and include a minimal reproduction.)

### What to expect

1. **Acknowledgment** within **48 hours** of your report.
2. **Triage** — we confirm the issue, scope its impact, and assign severity.
3. **Fix** — we develop and ship a patch. Timeline depends on severity:
   - **Critical / High**: patch as soon as possible (target within days).
   - **Medium / Low**: scheduled with the next release.
4. **Disclosure** — we coordinate public disclosure after the fix ships so
   users can upgrade before details go public.

If a report is declined (not a vulnerability, or out of scope), we explain why
and close it with that reasoning. We request that reporters allow time for a
patch before public disclosure.

## Security practices in this repo

- Secrets never ship in source or config — use environment variables / CI
  secrets only (see `.env.example` for the shape).
- External-service failures fail **open** (graceful degradation), never leak
  state.
- CI runs secret scanning and static analysis on PRs before merge.
- Dependencies are kept current; security advisories are triaged promptly.

[advisories]: https://github.com/ZyntroAI/fastapi-python-boilerplate/security/advisories

## Supply Chain: GitHub Actions SHA Pinning

Every GitHub Action used in `.github/workflows/` must be pinned to a **full
40-character commit SHA**. Version tags (`@v4`) and branch refs (`@main`,
`@master`) are rejected — a tag is mutable, so it can be moved to point at
different code without any change to this repository.

### Enforced automatically

The `verify-sha` job in `.github/workflows/ci.yml` runs first on every push and
pull request. It scans all workflow files and fails the build if any action is
referenced by tag or branch. `lint`, `test` and the remaining jobs wait on it.

Check locally at any time:

```bash
python3 .github/workflows/scripts/verify-shas.py
```

### Updating action versions

Never edit a pinned SHA by hand. Resolve it from the action's own repository:

```bash
export GITHUB_TOKEN=...        # needs `repo` + `workflow` scope
python3 pin_workflows.py --dry-run   # preview
python3 pin_workflows.py             # rewrite the workflow files
```

`pin_workflows.py` resolves each tag to its commit SHA via the GitHub API,
verifies the commit exists in the upstream repository, and rewrites only the
affected references. Nothing is resolved from a fork.

### Pin history

| Date       | Actions pinned | Scope                          | Notes                          |
| ---------- | -------------- | ------------------------------ | ------------------------------ |
| 2026-09-11 | 76 refs        | all 12 workflow files          | Initial enforcement; repaired 5 fabricated pins and 5 invalid YAML files |

When you run `pin_workflows.py` and merge the result, add a row to this table.
