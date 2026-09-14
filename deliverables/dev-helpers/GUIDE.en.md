# Dev-helpers guide — full reference

Four small tools for the friction points in automated GitHub work. Each one
solves a problem you currently learn the hard way. Each section follows the same
four-part shape: **the problem → the mechanism → usage → real gotchas**.

---

## 1. perm-checker — know a push will be rejected before you try it

### The problem

The work is finished and then the push fails:

```
! [remote rejected] fig/topic -> fig/topic
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/ci.yml` without `workflows` permission)
```

By then the turn is spent. The question worth asking first is "will this push be
accepted?"

### The mechanism

A push needs two layers of permission:

- **`contents: write`** — needed by every push.
- **`workflows: write`** — needed when the push touches a file under
  `.github/workflows/`. This is an **App-installation** permission; a
  repository-level write grant cannot supply it.

`check()` compares the changed paths against the permission map you hold and
returns whether `can_push`, plus exactly what is missing.

### Usage

```python
from dev_helpers import check_push, explain_push

report = check_push(
    {"contents": "write"},
    ["README.md", ".github/workflows/ci.yml"],
)
# report["can_push"]  -> False
# report["missing"]   -> [["workflows", "write"]]
print(explain_push(report))
```

For a markdown block to paste into a PR body:

```python
from dev_helpers import format_report
print(format_report(report))
```

### Real gotchas

- `".github/workflows/ci.yml".lstrip("./")` returns `"github/workflows/ci.yml"` —
  it **eats the leading dot**, because `str.lstrip` takes a *set of characters*,
  not a prefix. With that wrong strip, the `startswith(".github/workflows/")`
  test never matches and the tool wrongly reports the push will pass. Use
  `normalize_path()` instead.
- A permission value of `None` or `"none"` must count as **absent**, not present.
  The module handles this in `_level`.

---

## 2. ci-workflow — workflows that fail silently, and actions that are not pinned

### The problem

Two symptoms reported as "our CI is flaky" have entirely different causes:

1. **A file that does not parse** — the workflow never runs at all. GitHub shows
   no failure on the PR, so the gate looks green because it is *absent*, not
   because it passed.
2. **An unpinned action** — `uses: actions/checkout@v4` follows a tag. What runs
   in your build can change with no diff in your repository.

### The mechanism

- `scan_pins(text)` splits every `uses:` line into pinned / unpinned, counting a
  full 40-hex commit SHA as pinned (a trailing `# v4.2.2` comment is fine), and
  **skips** local actions (`./…`) and `docker://` refs — those are not
  third-party actions and must not be reported as unpinned.
- `parse_state(text)` attempts PyYAML when available and otherwise falls back to
  a structural check, always reporting which `engine` decided, so a lenient
  result is never mistaken for a thorough one.
- `scan_workflows(root)` walks the whole directory and returns one summary.

### Usage

```python
from dev_helpers import scan_workflows

audit = scan_workflows(".")
audit["count"]            # number of workflow files
audit["unpinned_total"]   # how many uses: still unpinned
audit["unparseable"]      # [{"file": ..., "error": ...}]
```

### Real gotchas

- **Never read "parses" as thorough when the engine is `structural`** — it is far
  more lenient than PyYAML, which is why the module always attaches `engine`.
- Local and `docker://` refs are not SHA-pinned actions. Without that exclusion
  the count is inflated and the report gets ignored.

---

## 3. approval-doc — write a request that can be granted in one reading

### The problem

When a push is blocked on permission, the useful artefact is not an error string
but a request someone can act on immediately: what is blocked, which files,
which permission, why the narrow grant is safe, and what to do instead if they
would rather not grant it.

### The mechanism

`build_approval_doc()` collects the facts into a dict; `render_markdown()`
renders a document that names repo/branch/requester, explains the block, quotes
the real GitHub rejection, lists the full change set, argues why the narrow
grant is safe, and offers **the alternative that needs no grant** — delivering
the change as a patch.

### Usage

```python
from dev_helpers import build_approval_doc, render_markdown

doc = build_approval_doc(
    repo="ZyntroAI/fastapi-python-boilerplate",
    branch="fig/dev-helpers-guide-suite",
    files=[".github/workflows/ci.yml"],
    permission="workflows",
    reason="CI gate is blocked at push.",
)
open("github-write-access-request.md", "w").write(render_markdown(doc))
```

### Real gotchas

- **Always include the alternative.** A request that only says "grant me this"
  reads as pressure; stating that the change can ship as a patch instead makes
  the grant an easier yes.
- Name the permission exactly (`workflows`, not `contents`). They are different
  gates and the approver has to find the right menu item.

---

## 4. pr-helper — a PR whose DoD gaps are visible

### The problem

Repos that enforce a Definition of Done tend to receive PRs that *assert* in
prose that the CHANGELOG was updated, with nothing making that true — and the
remaining DoD items quietly unmet.

### The mechanism

`checklist(facts)` builds the DoD checklist from facts:

- a name present with a truthy value → checked
- a string value → checked, with the value shown as evidence
- a name absent or falsey → **unchecked** (that is the point — the gap shows)

`build_pr_body()` assembles Summary / Changes / Verification / Definition of
Done / Notes.

### Usage

```python
from dev_helpers import build_pr_body

body = build_pr_body(
    summary="Add the dev-helpers suite.",
    files=["deliverables/dev-helpers/README.md"],
    tests="`python3 -m unittest` — 25 passed",
    dod_facts={"CHANGELOG.md updated": "PR #…"},
)
```

### Real gotchas

- **Never default to checked.** If an unmentioned item renders checked, the
  checklist carries no information. The correct default is unchecked.
- Use evidence that can be followed (a PR number, a command name) — not the word
  "done".

---

## Testing

```bash
cd deliverables/dev-helpers
python3 -m unittest discover -s dev_helpers/tests -t . -v
# Ran 25 tests ... OK
```

The tests cover every behaviour promised in `SKILL.md`, including the gotchas
above — notably the test asserting that `lstrip("./")` gives the wrong answer,
so it cannot quietly be reintroduced.
