# Problems — Open Issues & Known Blockers

Companion to [`CHANGELOG.md`](./CHANGELOG.md). The changelog records what
shipped; this file records what is **still wrong**, with the evidence behind it.

Entries are dated the same way as the changelog, so a `[2026-09-10]` section
here pairs with the `[2026-09-10]` section there. Each problem names the tracker
task that owns it, when one exists.

Status key: **OPEN** (unfixed) · **BLOCKED** (cannot be fixed from this
environment) · **RESOLVED** (fixed; kept briefly for context).

---

## [2026-09-11]

### P-009 — The root `tests/` suite never collects — OPEN

**Owner:** unassigned

`pytest tests/` dies in `conftest.py` before a single test is collected, so the
`Test` job in `ci.yml` and the `Run ALL Tests` job in `test-suite.yml` can never
pass — on `main` or on any PR.

`tests/conftest.py` does `from app.main import app`, which reaches
`app/core/config.py`, whose `Settings` declares `OAUTH_CLIENT_ID: str` as a
**required** field. Neither the tracked `.env` (it contains only BytePlus keys
and a stray documentation line) nor any workflow `env:` block supplies it.

**Evidence:**

```
$ pytest tests/ --collect-only -q
python-dotenv could not parse statement starting at line 2
ImportError while loading conftest '.../tests/conftest.py'.
tests/conftest.py:7: in <module>
    from app.main import app
app/main.py:3: in <module>
    from app.api import auth, callback, health
app/api/auth.py:6: in <module>
    from app.core.config import settings
app/core/config.py:68: in <module>
    settings = get_settings()
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
OAUTH_CLIENT_ID
  Field required [type=missing, input_value={}, input_type=dict]
```

`ci.yml` passes only `DATABASE_URL` to the pytest step; `test-suite.yml` passes
`DATABASE_URL`, `REDIS_URL`, `API_BASE_URL`, `COMPOSE_FILE`,
`COMPOSE_PROJECT_NAME`. Neither sets `OAUTH_CLIENT_ID`.

**Fix (one of):** give `OAUTH_CLIENT_ID` a default in `app/core/config.py`
(it is an OAuth *public* client id — a placeholder default is harmless), or set
it in the test invocation, or move it to `OAUTH_CLIENT_ID: str | None = None`
and raise at the login endpoint instead of at import. The last is the only one
that also unblocks importing the app in a worker/CLI context.

---

### P-010 — `app.api.routes` imports two modules that do not exist — OPEN

**Owner:** unassigned

`app/api/routes.py` cannot be imported at all:

```
from app.models.user_models import UserCreate, UserOut, TokenOut
from app.services.users import get_repo, fanout_profile
```

- `app/models/user_models.py` — does not exist (`app/models/` holds
  `dependency.py`, `graph_service.py`, `items.py`, `oauth_service.py`,
  `search_service.py`, `token_service.py`, `user_service.py`, `users.py`)
- `app/models/__init__.py` — does not exist, so `app.models` is not a package
  at all
- `app/services/users.py` — exists; the names `get_repo` / `fanout_profile`
  have not been checked against it

Separately, `tests/conftest.py` imports `get_current_user` from
`app.api.routes`, but that symbol is only re-exported there from
`app.api.auth`. It is defined in `app.core.deps` and `app.core.security`. So
even once P-009 is fixed, the import path in conftest is wrong.

**Evidence:** `python -c "import app.api.routes"` → `ModuleNotFoundError:
No module named 'app.models'`; `ls app/models/` as listed above.

**Note:** P-009 must be fixed first — it masks this one, because
`app.core.config` raises before the missing module is reached.

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

## [2026-09-11]

### P-009 — `release_drafter.yaml` is not a workflow and sits in `workflows/` — OPEN

**Owner:** `TASK-20260910-004`

`.github/workflows/release_drafter.yaml` parses as YAML but has no `on:` and no
`jobs:` — it is a release-drafter `autolabeler:` configuration, not a workflow.
It has been sitting in the workflows directory since it was added, and it is the
run named `.github/workflows/release_drafter.yaml` that shows as a failure on
`main`. GitHub cannot run it because there is nothing to run.

**Evidence:** `yaml.safe_load` yields `{'autolabeler': [...]}`, no `on`/`jobs`;
no workflow file in the repo references the path.

**Fix:** move it to `.github/release-drafter.yml` (done in the patch below). A
release-drafter *workflow* that consumes it does not exist yet — that is a
separate decision, not a repair.

---

### P-001 / P-002 — re-verified today, fix re-prepared against current `main` — BLOCKED

The fix described under `[2026-09-10]` was re-prepared against `main` at
`e34ede2`, because the tree has moved since it was first written. Current
numbers differ from the September 10 entry:

| | 2026-09-10 entry | re-verified 2026-09-11 |
| --- | --- | --- |
| Unpinned action refs | 66 | 23 |
| Files affected | 11 | 11 |
| Broken YAML files | 5 | 5 |

The five YAML failures are unchanged (`ci.yml`, `secret-scan.yml`,
`dependabot-automerge.yml`, `Auto-Index-Sync.yml`, `test-suite.yml`), so P-001
stands as written. The pinning fix now covers 23 distinct action refs including
the four `github/codeql-action/*` sub-paths, which the earlier count folded in.

**Evidence:** `yaml.safe_load` over all 11 workflow files — 0 parse failures
after repair; unpinned-ref scan returns empty. Patch applies clean to a fresh
clone of `main` (`git apply --check`), and `yaml.safe_load` re-run on the
applied tree still reports 0 failures.

**Deliverable:** `ci_sha_pin_workflow_fix.patch` (+ `.bundle`) — cannot be
pushed as a PR, see P-003.

---

## How to add an entry

1. Put it under the date section matching its changelog counterpart.
2. Give it an id (`P-NNN`), a one-line title, and a status.
3. Name the owning tracker task if there is one.
4. Include the evidence — the command and its actual output, not a description
   of what the command would say.
5. When fixed, mark it **RESOLVED**, say what fixed it, and leave it in place
   for one cycle before removing.
