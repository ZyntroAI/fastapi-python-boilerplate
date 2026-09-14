# 🧰 Skill: CI Workflow Authoring

**เขียน GitHub Actions workflow สำหรับ repo นี้ให้รันได้จริงตั้งแต่ครั้งแรก**

Everything here is checked against the repo as it stands, not written from a
template. The six failure modes below are ones that actually occurred in this
repository's workflows — each one produces a job that is *green-looking but
never ran*, which is the worst kind of CI bug.

---

## The six ways a workflow silently fails here

| # | Failure | What you see | Why |
| - | ------- | ------------ | --- |
| 1 | Not valid YAML | The workflow never appears in the Actions tab at all | Two documents pasted together (`preservedjobs:`), a heredoc, or an unquoted `:` in a string |
| 2 | Action not SHA-pinned | `Set up job` fails: *Unable to resolve action …* | Org policy requires a full 40-char commit SHA; `@v4` is rejected |
| 3 | SHA that does not exist | Same message, different cause | The SHA was invented or copied from another action's repo |
| 4 | Script or target missing | Job fails after checkout | `scripts/x.py`, `make ci`, `./charts` referenced but absent |
| 5 | Exit code read too late | `if [ $? -eq 0 ]` reports the **echo's** success | `$?` must be captured on the next line |
| 6 | `if: failure()` on a green-`needs` chain | Rollback/notify steps never fire | `needs: merge-queue` means the post-merge job does not run unless that job succeeded |

Rule 6 catches people constantly. A rollback step guarded by `if: failure()`
inside a job that only starts when its dependency *succeeded* can never roll
back the thing that failed.

---

## Hard rules for this repository

1. **SHA-pin every `uses:`.** Resolve and verify against the API first:
   ```bash
   gh api repos/actions/checkout/commits/v5 --jq .sha
   ```
   Then confirm the SHA belongs to *that* action's repo — a SHA from the wrong
   repo returns 422 and the job dies at setup.
2. **Quote any string containing `:`.** `foo: bar` inside a `run:` gets parsed as
   a mapping. Prefer a quoted single line or a `|` literal block.
3. **Check the artifact exists before referencing it.** `scripts/pr_triage_automove.py`
   is not in this repo; the automove entry point is
   `skills/pr-triage-automove/automove.py`.
4. **Check Make targets before calling them.** This Makefile has
   `setup install test lint format check run clean` — **there is no `ci` and no
   `smoke-test`**.
5. **Never `git push origin HEAD:main` from a `pull_request` job.** On a fork the
   token is read-only and the run dies; on a same-repo branch it bypasses review.
   Use `gh pr merge --auto` and let the platform do the gating.
6. **Report-only by default.** A workflow whose default path mutates the tree will
   surprise the first reviewer who meets it. Gate writes behind an explicit
   opt-in (a repository variable or a label).
7. **Verify writes landed.** This environment can reset files mid-task; re-read a
   file after writing it and before running the gate.

---

## The linter

```bash
python skills/ci-workflow-authoring/lint.py .github/workflows/*.yml
python skills/ci-workflow-authoring/lint.py path/to/anything.yml
```

Checks the layers an LLM-authored workflow actually fails at: YAML parse, required
top-level keys, per-job `runs-on`/`steps`/`uses-or-run`, SHA pinning, concatenated
documents, hardcoded credentials.

Exit `1` if anything failed, so it drops straight into CI.

### Running it against this repo today

```
FAIL .github/workflows/ci.yml            not SHA-pinned: actions/checkout@v4 …
FAIL .github/workflows/test-suite.yml    not SHA-pinned: …
```

Every failing workflow in this repo fails for reason **#2 or #3** — a tag pin or
an unresolvable SHA — which is why every PR currently shows red checks regardless
of its diff.

---

## Examples

`examples/` holds three corrected workflows, each annotated at the points where
the pasted version broke:

- **`pr-triage-automove.yml`** — runs the real `skills/pr-triage-automove/automove.py`,
  report-only, SHA-pinned, and it does **not** claim success when nothing was
  checked.
- **`merge-queue.yml`** — uses `gh pr merge --auto` instead of pushing to `main`,
  and reads check conclusions from the API rather than from `$?`.
- **`post-merge.yml`** — deploys the chart that exists (`helm/oauth-app`), reads
  `$?` on the right line, checks the secret is present, and rolls back by revision.

---

## Before you commit a workflow

```bash
# 1. does it parse, and is every action pinned?
python skills/ci-workflow-authoring/lint.py <file>.yml

# 2. do the things it runs actually exist?
grep -nE "^[a-z-]+:" Makefile                 # targets
ls scripts/ skills/                           # scripts
ls helm/ charts/                              # charts

# 3. do the SHAs resolve?  (lint.py only checks that a pin LOOKS like a SHA)
python skills/ci-workflow-authoring/verify-pins.py .github/workflows/*.yml
```

Step 3 is the one that matters most, and the one `lint.py` cannot do. A
fabricated 40-hex string satisfies every pattern check and still fails at
`Set up job` with "Unable to find version", so a green lint is not evidence the
pins are real. `verify-pins.py` asks GitHub whether each commit exists in **that
action's own repository** and exits non-zero if any does not.

It uses the HTML commit endpoint rather than the REST API, because the anonymous
API allows 60 requests/hour — enough to exhaust halfway through a repository of
any size. Two details it handles:

- **subdirectory actions** (`owner/repo/subdir@sha`) are looked up against
  `owner/repo`; querying the three-segment path 404s even for a real commit
- **a network error is reported as unverifiable, not as fake** — an unreachable
  GitHub is not evidence about a SHA

If a check cannot run in your environment (no `workflows` permission to push),
say so in the PR — do not report it as passing.
