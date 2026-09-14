# 🧾 Skill: PR Full Lifecycle Workflow

**ตั้งแต่ branch แรกจนถึง monitor หลัง merge — validation ทำงานคู่กัน ไม่ใช่ต่อคิว**

A PR is not "opened, reviewed, merged". It is six stages with a gate at each, and
the gates that matter most are the ones that stop a bad merge rather than the
ones that describe a good one.

---

## When this applies

- Setting up CI for a repo that has none, or replacing a workflow that never ran.
- A PR sat red for days because one unrelated job could not start.
- Deciding whether to add a merge queue, auto-merge, or deploy-on-merge.

Not for: a one-file docs change on a repo with working CI.

---

## The stages

### 1. Planning

Branch naming carries intent and lets CI branch on it: `feat/*`, `fix/*`,
`chore/*`, `docs/*`. Conventional Commits for messages, so the changelog and
release tooling can derive versions without a human.

### 2. Development

Local gate before the push, and the same gate in CI — the two must not drift:

```bash
make check        # format + lint + test, the same target CI calls
```

A `Makefile` target that CI invokes is worth more than a CI-only script: it is
runnable by a person, which is how you debug a red job.

### 3. Review

Split by file path, not by round-robin. Backend paths to the backend owner,
frontend to the frontend owner — a reviewer who owns the change reviews faster
and more accurately than one assigned by rotation.

### 4. Testing

Matrix the independent jobs and let them run **in parallel**, with dependency
caching. Serialising lint behind tests buys nothing and triples the wall clock.

### 5. Merge

Auto-merge only behind a **check-run gate**, never on approval alone. A merge
queue serialises merges so two green PRs cannot produce a red main.

### 6. Post-merge

Deploy, then smoke-test, with rollback reachable **before** the deploy is
declared done. Notify a channel so the deploy is visible to people not watching
Actions.

---

## Workflow — the parts that are usually wrong

```yaml
name: PR Full Lifecycle

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read            # start from least privilege; widen per job

concurrency:                # a new push cancels the previous run
  group: pr-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  validate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    strategy:
      fail-fast: false      # one red job must not hide the other two
      matrix:
        task: [lint, test, security]
    steps:
      - uses: actions/checkout@<40-char-sha>
      - uses: actions/setup-python@<40-char-sha>
        with:
          python-version: "3.11"
          cache: pip          # cache belongs on the toolchain, not hand-rolled
      - run: pip install -r requirements-dev.txt
      - run: make ${{ matrix.task }}

  auto-merge:
    needs: validate
    if: contains(github.event.pull_request.labels.*.name, 'auto-merge')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      checks: read
    steps:
      - run: gh pr merge --squash --auto "$PR"
        env:
          PR: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Four things doing real work there:

- `fail-fast: false` — otherwise a lint failure cancels the test job and you
  never see that the tests were also red.
- `concurrency` with `cancel-in-progress` — stale runs on an old commit waste
  runners and can report green after a newer push went red.
- `permissions` at workflow level, widened per job — the default token is
  broader than any of these jobs needs.
- Auto-merge keyed on a **label plus the check gate**, never on the event alone.

## Gotchas earned in practice

- **Every `uses:` pins to a full 40-char SHA, not `@v4`.** A tag is mutable; a
  release can move under you. Pinning is the difference between a reproducible
  run and one that changes without a commit.
- **A workflow file that is not valid YAML does not fail — it does not run.**
  No error on the PR, just a missing check. Verify every workflow parses
  (`python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" file.yml`)
  and treat "expected check never appeared" as a workflow bug, not a settings one.
- **A check named in branch protection that no job produces blocks every merge.**
  Keep required-check names and job names in sync; renaming a job silently
  un-gates the branch.
- **Auto-merge without a check gate merges on approval.** Wire it to the check
  run, or it ships unreviewed test failures.
- **`matrix.fail-fast` defaults to true.** Most matrixes want it false.
- **Deploy targets are not test targets.** Never point a PR workflow at
  production credentials; integration tests that need them stay opt-in.

## Output

The workflow file, the `Makefile` targets it calls, and branch-protection
settings whose required checks match the job names. Verify by opening a throwaway
PR and confirming each expected check appears — a workflow that parses is not the
same as a workflow that runs.
