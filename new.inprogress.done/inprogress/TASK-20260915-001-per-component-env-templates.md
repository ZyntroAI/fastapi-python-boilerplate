---
id: TASK-20260915-001
title: Per-component env templates and environment documentation
status: inprogress
priority: normal
created: 2026-09-15
updated: 2026-09-15
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [231]
blocked_by:
tokens: 6827
---

# TASK-20260915-001 — Per-component env templates and environment documentation

## Goal

Every component that reads environment variables ships a `.env.example`
beside its code, `.env` is ignored everywhere while templates are tracked, and
`docs/ENVIRONMENT.md` explains the layout — so a contributor can configure the
repository without reading source, and no env key the code needs is
undocumented.

## Scope

- Add `.env.example` for each component that reads env: `graphql_api/`,
  `frontend/`, `scripts/`, `deliverables/{pm-backend,
  fastapi-obsidian-backend, agent-security-suite, manus-client}`,
  `deliverables/product-crud/{server,web}`.
- Rewrite the root `.env.example`: grouped by concern, each variable annotated
  with the file that reads it.
- Fix `.gitignore` so env templates are tracked.
- Add `docs/ENVIRONMENT.md` and `scripts/validate_env_templates.py`.
- Re-resolve the `.env` modify/delete conflict against current `main`.

## Out of scope

- **Rotating any credential.** The history scan for real-looking values
  returned zero, so rotation is not required; and rotation is an owner
  decision regardless.
- **Deleting `.env` from history.** A history rewrite on a public repository
  is destructive and needs owner sign-off.
- **Removing the tracked `.env` in
  `deliverables/fig-best-practices/examples/broken-project/`.** It is a test
  fixture the quality gate asserts on. Removing it would make a passing test
  vacuous.
- **Repairing the five unparseable workflows (P-001).** Unrelated known defect;
  needs `.github/workflows/` write access the automation App does not hold.
- **The reserved keys** (`VAULT_ADDR`, `VAULT_ROLE`, `ALERT_SLACK_WEBHOOK`).
  No code reads them; they are labelled as such rather than deleted, so the
  broker/Vault rollout has a landing spot.

## Steps

- [x] Reproduce the conflict: branch deleted `.env`, `main` modified it
- [x] Resolve and confirm `git merge-base --is-ancestor origin/main HEAD`
- [x] Inventory every env var the repo reads, grouped by component
- [x] Author 10 per-component templates + rewrite the root template
- [x] Fix the `.gitignore` `.env.*` rule that swallowed the new templates
- [x] Write `docs/ENVIRONMENT.md`
- [x] Add `scripts/validate_env_templates.py` and drive it to 0/0
- [x] Record in `CHANGELOG.md`
- [ ] Owner review of PR #231

## Acceptance criteria

- [x] Every template parses; keys well-formed and unique; no value looks like a
      real secret.
- [x] Every declared key resolves to a real read in the component it documents,
      except keys explicitly marked Reserved.
- [x] All 23 vars read by `app/` are documented in the root template.
- [x] `.env` is still ignored at every level (`git check-ignore -v`).
- [x] Per-component `.env.example` files are NOT ignored — the specific bug
      that made the first attempt of this work invisible to git.
- [x] `python3 scripts/validate_env_templates.py` exits 0.

## Dependencies / blockers

None for what is in scope. PR #231 remains a draft and carries two
`CHANGES_REQUESTED` reviews from `zyntromedia` — the owner's review is what
closes it.

## Files changed

| File | Change |
| --- | --- |
| `.env` | Deleted — resolved the modify/delete conflict by keeping the untrack |
| `.env.example` | Rewritten — grouped, annotated, complete for the core app |
| `.gitignore` | Negations so env templates are tracked |
| `docs/ENVIRONMENT.md` | Added |
| `scripts/validate_env_templates.py` | Added |
| `graphql_api/.env.example` | Added |
| `frontend/.env.example` | Added |
| `scripts/.env.example` | Added |
| `deliverables/pm-backend/.env.example` | Added |
| `deliverables/fastapi-obsidian-backend/.env.example` | Added |
| `deliverables/agent-security-suite/.env.example` | Added |
| `deliverables/manus-client/.env.example` | Added |
| `deliverables/product-crud/server/.env.example` | Added |
| `deliverables/product-crud/web/.env.example` | Added |
| `CHANGELOG.md` | Entry for PR #231 |

## Validation

| Command | Result |
| --- | --- |
| `python3 scripts/validate_env_templates.py` | `0 failures, 0 warnings`, exit 0 |
| `git check-ignore -v --no-index <each>.env.example` | no match — all 11 trackable |
| `git check-ignore -v --no-index .env` | `.gitignore:48:.env` — still ignored |
| `git merge-base --is-ancestor origin/main HEAD` | true |
| `gh api .../pulls/231` | `mergeable: true` |

## Token usage

Estimated with `len(text) // 4` over the files above: **6827**. This is a size
proxy, not a measured API figure.

## Notes

The `.gitignore` rule was the load-bearing find. `.env.*` matched
`.env.example` at every depth, so the per-component templates this task adds
would have been written to disk, silently ignored by git, and never committed —
the exact failure mode where the work looks done locally and the PR is empty.
`git check-ignore -v --no-index` is what exposed it; `git status` showed a clean
tree, which is the misleading signal.

Two undocumented gaps were closed while inventorying:

- `app/core/config.py` declares `JWT_SECRET` and `app/config.py` declares
  `JWT_SECRET_KEY`, both reading the same `.env`. Setting only one makes login
  succeed while every subsequent token fails verification. Both are now in the
  template with that warning attached.
- `SENTRY_DSN`, `CACHE_ENABLED`, `CACHE_TTL` had no template entry at all.

`scripts/validate_env_templates.py` is the reason the checks above are
re-runnable by anyone rather than asserted from an author's workspace. It found
the four missing vars only after its detection was widened to cover
`pydantic-settings` field declarations and Prisma's `env("...")` — a narrower
scanner reported a clean pass over vars that were in fact undocumented.

## Completion summary

Open — pending owner review of PR #231.
