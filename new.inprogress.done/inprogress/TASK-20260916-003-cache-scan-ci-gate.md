---
id: TASK-20260916-003
title: Wire the cache scan in as an advisory CI gate
status: inprogress
priority: normal
created: 2026-09-16
updated: 2026-09-16
owner:
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by:
tokens: 0
---

# TASK-20260916-003 — Wire the cache scan in as an advisory CI gate

## Goal

The cache-footprint audit (`cache_reduction scan`) currently runs only when
someone remembers to run it. After this ships it runs on every push to `main`
and `dev` and on every PR to `main`, publishing its findings to the job summary
and as a downloadable artifact — without ever blocking a merge.

## Scope

- Vendor the `cache-reduction` toolkit into `deliverables/cache-reduction-skill/`.
- Add `.github/workflows/cache-scan.yml` as an advisory job.
- Document the scan, its scope, and how to promote it to a blocking gate.

## Out of scope

- Making the job blocking. The repo's current tree carries findings, so a
  blocking gate could never go green. The promotion path is documented instead.
- Fixing the findings themselves (`app/core/performance.py:35`, the two
  `@lru_cache` sites). That is follow-up work.
- The CR2xx agent-context rules over `docs/` and `Skills/`. Scope is `app/`.

## Steps

- [x] Confirm the scan command and exit-code contract against `app/`.
- [x] Vendor the toolkit onto `ci/cache-scan-gate`.
- [x] Author the advisory workflow with SHA-pinned refs.
- [x] Validate: YAML parse, repo pin verifier, dry-run the scan step.
- [ ] Push branch and open the PR.
- [x] CHANGELOG + task record.

## Acceptance criteria

- [x] `cache_reduction scan app/` exits 1 when a high finding is present and 0
      when it is not.
- [x] The toolkit's own 41 tests pass from their vendored location.
- [x] `verify_workflows.py` reports no problem for `cache-scan.yml`.
- [x] Every `uses:` in the new workflow is a real 40-hex SHA already verified
      by the repo's own repair set.
- [x] The job cannot fail a build: every finding-bearing step is
      `continue-on-error: true`.
- [ ] Branch pushed and PR open.

## Dependencies / blockers

None for the files under `deliverables/`. The workflow file itself is subject to
the known Fig GitHub App `workflows`-scope block.

## Files changed

| File | Change |
| --- | --- |
| `deliverables/cache-reduction-skill/` | Added — vendored toolkit (package, tests, README, pyproject) |
| `.github/workflows/cache-scan.yml` | Added — advisory cache-scan job |
| `CHANGELOG.md` | Modified — 2026-09-16 entry |
| `new.inprogress.done/inprogress/TASK-20260916-003-cache-scan-ci-gate.md` | Added |

## Validation

| Command | Result |
| --- | --- |
| `python3 -m pytest -q` in `deliverables/cache-reduction-skill` | 41 passed |
| `python3 -m cache_reduction scan app/` | 3 findings, exit 1 |
| `python3 deliverables/ci/verify_workflows.py` (filtered to `cache-scan`) | CLEAN — no problem reported for the new file |
| `yaml.safe_load('.github/workflows/cache-scan.yml')` | parses; 1 job, 6 steps |

## Token usage

Estimated with `len(text) // 4` over the files above: **0**. This is a size
proxy, not a measured API figure.

## Notes

Why advisory rather than blocking: run against the repo's own `app/` tree the
scan reports three findings, and at least two of them are false positives —
`redis.setex(key, ttl, value)` passes its TTL as a variable, which the numeric
TTL regex does not recognise, and `@lru_cache()` on the zero-argument
`get_settings()` cannot grow without bound. A blocking gate on the current tree
would be red from the first run. The workflow carries that reasoning in a header
comment and explains the one-line promotion path.

## Completion summary

Fill in only when moving to `done/` or `archive/`.
