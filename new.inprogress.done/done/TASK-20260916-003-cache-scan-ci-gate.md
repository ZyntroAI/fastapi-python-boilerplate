---
id: TASK-20260916-003
title: Wire the cache scan in as an advisory CI gate
status: done
priority: normal
created: 2026-09-16
updated: 2026-09-16
owner:
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [318]
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
- [x] Push branch and open the PR (#318).
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
- [x] Branch pushed and PR open (#318). The workflow file itself is
      handed off in a PR comment — the App lacks the `workflows` scope.

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

The cache scan is wired in as an advisory job. `deliverables/cache-reduction-skill/`
now carries the toolkit (41 tests passing from its vendored location) and
`.github/workflows/cache-scan.yml` runs `cache_reduction scan app/` on every push to
`main`/`dev` and every PR to `main`, writing findings to the job summary and
uploading `cache-scan.json`. Every finding-bearing step is `continue-on-error`, so
the job reports without ever failing a build — deliberate, because the scan
currently reports three findings against `app/`, at least two of which are false
positives (`setex` with a variable TTL; `@lru_cache` on a zero-argument getter).

Delivered as PR #318. The workflow file could not be pushed: the GitHub App lacks
the `workflows` scope, and the remote refused the ref with "refusing to allow a
GitHub App to create or update workflow ... without `workflows` permission". A
discriminator push of the same commit minus that file succeeded, pinning the block
to the App permission rather than credentials or branch rules. The file is handed
off verbatim in a PR comment for a maintainer to apply.

Follow-up: clear the three findings (or tighten the two rules), then flip
`continue-on-error` off to promote the job to a real gate.
