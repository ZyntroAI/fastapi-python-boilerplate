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
