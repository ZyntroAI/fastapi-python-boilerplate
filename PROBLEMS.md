# Problems — Open Issues & Known Blockers

Companion to [`CHANGELOG.md`](./CHANGELOG.md). The changelog records what
shipped; this file records what is **still wrong**, with the evidence behind it.

Entries are dated the same way as the changelog, so a `[2026-09-10]` section
here pairs with the `[2026-09-10]` section there. Each problem names the tracker
task that owns it, when one exists.

Status key: **OPEN** (unfixed) · **BLOCKED** (cannot be fixed from this
environment) · **RESOLVED** (fixed; kept briefly for context).

---

## [2026-09-10]

### P-001 — CI is red repo-wide: 5 workflow files do not parse — OPEN

**Owner:** `TASK-20260910-004`

Five files in `.github/workflows/` are not valid YAML, so GitHub never runs
them. This is separate from the pinning problem (P-002): even fully pinned,
these files would fail.

| File | Parser error |
| --- | --- |
| `ci.yml` | `while parsing a flow mapping` — `{python-version: ${{ … }}}` is invalid flow-map syntax (3 sites) |
| `secret-scan.yml` | `while scanning a simple key` — `workflow_dispatch;` uses `;` not `:` |
| `dependabot-automerge.yml` | `while scanning a simple key` — 86 lines of GitHub documentation prose appended after valid YAML |
| `Auto-Index-Sync.yml` | `while scanning a simple key` — heredoc body at column 0 terminates the `run: \|` block scalar |
| `test-suite.yml` | `expected a single document in the stream` — the workflow is wrapped in markdown + a ```yaml fence |

**Evidence:** `yaml.safe_load` over every workflow-shaped file reports 5 failures.

**Fix:** prepared and verified, but cannot be pushed — see P-003.

---

### P-002 — 66 action refs are unpinned, which the org policy rejects — BLOCKED

**Owner:** `TASK-20260910-004`

The org requires every action reference to be a full-length commit SHA. 66 refs
still use movable tags (`@v4`, `@v5`, …), so every workflow fails at
*Set up job* with:

```
The actions actions/checkout@v4, actions/setup-python@v5, … are not allowed
in ZyntroAI/fastapi-python-boilerplate because all actions must be pinned to a
full-length commit SHA.
```

This is the reason `main` itself is red, and why PRs show `UNSTABLE`.

**Evidence:** 66 matches for `uses: …@(vN|main|latest)`; failure reproduced in
run logs for the current `main` HEAD.

**Fix:** prepared and verified (76 refs pinned across 11 files, 0 unpinned
remaining, `ci.yml` line endings preserved), but cannot be pushed — see P-003.

---

### P-003 — The automation App cannot write `.github/workflows/` — BLOCKED

**Owner:** `TASK-20260910-004`

Every attempt to push a branch touching `.github/workflows/` is rejected by the
remote:

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/<file>` without `workflows` permission
```

**This is not a token or grant problem.** It was isolated by a control test: a
branch touching no workflow file pushes fine, while a branch touching a workflow
file is rejected in the same session. The `workflows` scope is
installation-scoped and only an org owner can enable it, in two separate steps
(App permission, then installation approval).

**Impact:** P-001 and P-002 cannot be delivered as a PR from here. A verified
patch is attached to the request instead; an admin applies it, or the scope is
granted and the push is retried.

---

### P-004 — `agent-core` is unverified against a real provider and Supabase — OPEN

**Owner:** `TASK-20260910-005`

`deliverables/agent-core/` ships with 25 passing tests, but all of them run
offline against `httpx.MockTransport`. Nothing has been exercised against live
infrastructure:

| # | Unverified | Why it matters |
| --- | --- | --- |
| 1 | `AGENT_BASE_URL` default (`https://api.agent.ai/v2`) | Placeholder — never called |
| 2 | `submit()` reads `body["task_id"]`, `status()` reads `body["status"]` | A provider using `id`/`state` fails immediately |
| 3 | `schema.sql` never applied to a real project | The table may not exist as written |
| 4 | RLS policy never tested with two users | Cross-tenant isolation is unproven |
| 5 | `examples/agent-core-ci.yml` never ran on Actions | `uvicorn agent_core.api:app` never loaded for real |

**Evidence:** test suite is entirely `MockTransport`-based; no credential or
Supabase project was available.

**Note:** "25 tests pass" is not evidence of production readiness. Do not
describe this deliverable as production-ready until the five rows above pass.

---

### P-005 — `new-crystalcastle` has a bare `feat` branch that blocks `feat/*` pushes — OPEN

**Owner:** `TASK-20260910-003`

The remote holds a branch named exactly `feat`. Git cannot store both
`refs/heads/feat` and `refs/heads/feat/<name>`, so **any** `feat/...` branch
push fails with `directory file conflict` — which looks like a content
conflict but is not.

**Evidence:** reproduced on two independent clones (shallow and full); the same
commit pushed cleanly under a branch name without the `feat/` prefix.

**Fix:** delete or rename the bare `feat` branch, or push under a different
prefix. `TASK-20260910-003` is already `inprogress` on a non-`feat/` branch name.

---

### P-006 — `cmd_new` copied the template's `status:` comment — RESOLVED

Fixed in PR #179. `TASK_TEMPLATE.md` annotated `status: new` with a trailing
comment, and `cmd_new` copied that line verbatim into new task files. The value
then failed the folder/status check and broke three tracker tests that read the
template directly. The template now carries a bare value and `cmd_new`
normalises the line. Tracker tests: 20 passed.

Recorded here because the same class of bug — a template comment leaking into
generated content — can reappear if the template is annotated again.

---

### P-007 — `new-crystalcastle` CI: five workflows read a `requirements.txt` that does not exist at the root — OPEN

**Owner:** `TASK-20260910-006`

Five workflows in `new-crystalcastle` run `pip install -r requirements.txt`, but
the repository has no root `requirements.txt` — the only one is
`scripts/errorlog-generator/requirements.txt`. Every job fails immediately:

```
ERROR: Could not open requirements file:
[Errno 2] No such file or directory: 'requirements.txt'
##[error]Process completed with exit code 1.
```

Affected workflows: `FastAPI_CI.yaml`, `Python-CI.yml`,
`crystalcastle-coderabbit-test.yml`, `errorlog-generator.yml`, `test.yml`.

**Evidence:** failure log for run `34471137096` on `main` (2026-09-10);
`find . -name 'requirements*.txt'` returns only the `scripts/` path.

**Note:** this is a **separate cause** from the bad-SHA problem in
`TASK-20260910-003`. Fixing the codeql SHAs alone will not turn this repo's CI
green.

**Fix:** either add a root `requirements.txt`, or point each workflow at the
real path (or at `pyproject.toml`). Which one is correct depends on the intended
project layout — needs the owner's decision, not a guess.

---

### P-008 — `TASK-20260910-004` was stored in a file named `example-task.md` — RESOLVED

Fixed in PR #182. The tracker's example file had been overwritten in place with
a real task while keeping the placeholder filename, so the id in the
front-matter (`TASK-20260910-004`) did not match the path. Renamed to
`TASK-20260910-004-repair-github-actions-workflows.md`. Recorded because the
same mistake — reusing a template file for live content — will hide a task from
anyone browsing by filename.

---

## How to add an entry

1. Put it under the date section matching its changelog counterpart.
2. Give it an id (`P-NNN`), a one-line title, and a status.
3. Name the owning tracker task if there is one.
4. Include the evidence — the command and its actual output, not a description
   of what the command would say.
5. When fixed, mark it **RESOLVED**, say what fixed it, and leave it in place
   for one cycle before removing.
