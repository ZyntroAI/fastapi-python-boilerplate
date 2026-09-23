---
id: TASK-20260923-001
title: pg_trgm typo-tolerant search — runnable SQL test script + Thai guide
status: new
priority: normal
created: 2026-09-23
updated: 2026-09-23
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by:
tokens: 0
---

# TASK-20260923-001 — pg_trgm typo-tolerant search

## Goal

Ship a self-contained, re-runnable SQL script that exercises PostgreSQL
`pg_trgm` typo-tolerant search end to end (extension config, `similarity()`,
the `%` operator, threshold tuning, GIN indexing, `word_similarity`), plus a
Thai guide explaining each section. After this ships, anyone can test trigram
search directly in PostgreSQL without depending on the Fig Search tool.

## Scope

- `deliverables/pg-trgm-typo-tolerant-search/pg_trgm_typo_tolerant_search.sql`
  — 8-section script with 12 self-checking assertions.
- `deliverables/pg-trgm-typo-tolerant-search/README.md` — Thai section-by-section guide.

## Out of scope

- No application wiring — the suite is a standalone diagnostic, not an app feature.
- No CI workflow: a push touching `.github/workflows/**` is refused for the Fig App.
- No changes to existing schema, migrations, or `deliverables/agent-core/schema.sql`.

## Steps

- [x] Write the 8-section SQL script with assertions.
- [x] Run it against a real PostgreSQL 17 instance; fix the `LOAD` issue.
- [x] Correct the index and normalization sections to match observed behaviour.
- [x] Write the Thai README.
- [x] Verify byte-level consistency between README and script.

## Acceptance criteria

- [x] Script runs clean on a fresh database with `ON_ERROR_STOP on`.
- [x] Script is idempotent — a second run on the same database produces no errors.
- [x] All 12 assertions pass.
- [x] README names, values and counts match the script.

## Dependencies / blockers

None.

## Files changed

| File | Change |
| --- | --- |
| `deliverables/pg-trgm-typo-tolerant-search/pg_trgm_typo_tolerant_search.sql` | Added |
| `deliverables/pg-trgm-typo-tolerant-search/README.md` | Added |

## Validation

| Command | Result |
| --- | --- |
| `psql -d pgtrgm_repo -f deliverables/pg-trgm-typo-tolerant-search/pg_trgm_typo_tolerant_search.sql` | 12 passed / 0 failed / 12 total |
| second run on the same database | identical result, no errors |
| `EXPLAIN` on the 20k-row `big_users` table | `Bitmap Index Scan on idx_big_users_name_trgm` |

## Token usage

Estimated with `len(text) // 4` over the files above: **7150**. Size proxy, not
a measured API figure.

## Notes

Three findings that mattered and are documented in the README:

1. `LOAD 'pg_trgm'` is required — `CREATE EXTENSION IF NOT EXISTS` skips the
   extension's own SQL when it already exists, so the GUCs are never registered
   and a second run fails with `unrecognized configuration parameter`.
2. On small tables the planner picks a Seq Scan — that is cost, not a broken
   index. Seeing a Bitmap Index Scan needs enough rows (20k used here).
3. `similarity()` already ignores case and leading/trailing whitespace; what
   actually moves the score is inner whitespace and accents.

## Completion summary

Fill in when moving to `done/` or `archive/`.
