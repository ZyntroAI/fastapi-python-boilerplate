# Security Policy

This is the security policy for the ZyntroAI repositories. It covers how to report
a vulnerability, what is in scope, and the supply-chain rules the CI enforces.

## Supported versions

The project follows the FastAPI + Python support windows. Only actively maintained
lines receive security patches.

| Branch / Version       | Python      | FastAPI base | Supported       | Security updates  |
| ---------------------- | ----------- | ------------ | --------------- | ----------------- |
| `main` -> v1.x (latest)| 3.10 - 3.13 | >= 0.110.x   | Active          | Critical + High   |
| `v0.104.x` LTS         | 3.9 - 3.12  | 0.104.x      | Maintenance     | Critical only     |
| `v0.100.x`             | 3.8 - 3.11  | 0.100.x      | End-of-Life     | None              |
| `<= 0.99.x`            | any         | <= 0.99.x    | Unsupported     | None              |

When a version reaches end-of-life, no further patches are issued. Upgrade to a
supported line.

## Reporting a vulnerability

**Do not open a public GitHub Issue for a security problem** — that exposes the
issue before a fix is ready.

Report privately via either channel:

- **GitHub private advisory** (preferred) — `Security` -> `Report a vulnerability`
  in the repository.
- **Email** — `security@zyntro.ai`.

Please include: a clear description of the vulnerability type, minimal
reproduction steps or a proof-of-concept, the impact an attacker could achieve,
a CVSS score if known, the affected versions (first vulnerable and latest
confirmed), and a suggested fix or mitigation if you have one.

### Response SLA

| Phase              | Timeline             | Action                                            |
| ------------------ | -------------------- | ------------------------------------------------- |
| Acknowledgement    | <= 48 hours          | Confirm receipt, assign a tracking ID             |
| Triage             | <= 5 business days   | Validate, assign severity, confirm scope          |
| Fix development    | <= 90 days maximum   | Patch prepared, tested, validated                 |
| Advisory release   | on patch day         | Fixed release and advisory published together     |

We work with you on a coordinated release and credit valid reports in the
advisory. Low-risk reports may be grouped into the regular release cycle. If we
decline a report we explain why — out of scope, already patched, or requiring a
non-recommended configuration.

## Scope

**In scope:** authentication and authorization bypasses; injection (SQL, NoSQL,
command, XSS); secrets committed to code or config; dependency supply-chain
issues; insecure defaults; broken access control / IDOR; SSRF; missing or weak
encryption of data at rest.

**Out of scope:** versions marked unsupported above; denial-of-service and
brute-force against rate-limited endpoints; social engineering, phishing, or
physical access; vulnerabilities in upstream dependencies (report those
upstream); already publicly disclosed issues; anything requiring the user's own
machine to be compromised or a non-standard deployment.

## Disclosure policy and safe harbor

We practice coordinated vulnerability disclosure. If you report in line with this
policy we will not pursue legal action, provided you allow at least 90 days
before public disclosure, do not share details with third parties during the fix
window, and do not access or modify other users' data.

Disclosure timeline: report received -> acknowledged within 48 hours; triage
complete -> estimated fix date shared; patch ready -> advisory drafted privately;
release -> fix and advisory published together.

## Severity handling

| Severity | CVSS      | Response deadline | Example impact                            |
| -------- | --------- | ----------------- | ----------------------------------------- |
| Critical | 9.0-10.0  | 7 days            | Remote code execution, full compromise    |
| High     | 7.0-8.9   | 14 days           | Privilege escalation, data breach         |
| Medium   | 4.0-6.9   | 30 days           | Partial data exposure                     |
| Low      | 0.1-3.9   | next release      | Informational / hardening                 |

## Supply chain: GitHub Actions SHA pinning

Every GitHub Action referenced in `.github/workflows/` must be pinned to a **full
40-character commit SHA**. Version tags (`@v4`) and branch refs (`@main`,
`@master`) are rejected: a tag is mutable, so it can be moved to point at
different code with no change to this repository.

**Current state (verified against `main`, 2026-09-12):**

- SHA-pinning is **policy, not yet enforced by CI**. `ci.yml` has no
  `verify-sha` job and there is no `.github/workflows/scripts/verify-shas.py`;
  an earlier revision of this document described both as if they existed. A
  handful of references are already pinned; the majority are still tags
  (`actions/checkout@v4` x18, `actions/upload-artifact@v4` x11,
  `actions/setup-python@v5` x8, `github/codeql-action/*@v3`, `subosito/flutter-action@v2`,
  `somaz94/compress-decompress@v1`, `docker/*` and others).
- Six workflow files are not valid YAML as committed and therefore never run:
  `ci.yml`, `secret-scan.yml`, `Auto-Index-Sync.yml`, `dependabot-automerge.yml`,
  `test-suite.yml`, and `github-actions-autodebug-autorerun` (which also lacks a
  `.yml`/`.yaml` extension).
- Because jobs cannot start, a pull request shows red checks even when its own
  tests pass locally.

**Tooling.** `pin_workflows.py` resolves every tag or branch reference to a full
commit SHA via the GitHub API, verifies the commit exists upstream (never from a
fork), and rewrites only the affected lines:

```bash
python3 pin_workflows.py --dry-run   # preview
python3 pin_workflows.py             # rewrite the workflow files
```

The rewrite touches `.github/workflows/`, which the automation App is not
permitted to write — it must be applied by a maintainer, or after the App is
granted the `workflows` permission.

**Reference SHAs** (tags resolved to commits, 2026-09-12) for the actions
`ci.yml` uses:

```yaml
uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262        # v4
uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065    # v5
uses: codecov/codecov-action@b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238  # v4
uses: github/codeql-action/init@faaca9a8f6edddba5725ffe5adefdab6669a2eca     # v3
uses: github/codeql-action/analyze@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9     # v3
uses: docker/build-push-action@ca052bb54ab0790a636c9b5f226502c73d547a25 # v5
```

### Pin history

| Date       | Actions pinned | Scope             | Notes                                                            |
| ---------- | -------------- | ----------------- | ---------------------------------------------------------------- |
| 2026-09-12 | policy drafted | all workflow files| Policy documented; enforcement (CI gate + rewrite) still pending. |

When a maintainer runs `pin_workflows.py` and merges the result, add a row here.

## Repository security practices

- Secrets live in environment variables and CI secrets only — never in source.
  `.env` is untracked; a safe `.env.example` documents the required keys.
- Dependencies are kept current and advisories triaged promptly (Dependabot).
- CodeQL runs as part of the security job once the workflow files are valid.
- External-service failures fail open (graceful degradation).

[advisories]: https://github.com/ZyntroAI/fastapi-python-boilerplate/security/advisories
