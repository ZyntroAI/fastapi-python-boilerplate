# Task Tracking (`new` / `inprogress` / `done`)

A folder-based task tracker at the repository root. A task's **folder is its
status**, so progress is visible in a file listing — no tooling required.

> This is documentation and process only. It contains no application code and
> changes nothing under `app/`, `tests/`, or the project's configuration.

## The three statuses

| Folder | Status | Means |
| --- | --- | --- |
| `new/` | Not started | The work is understood but not begun. May be blocked. |
| `inprogress/` | In progress | Started, not finished. Open work is listed in the task. |
| `done/` | Done | Finished **and verified** — see Definition of Done. |

A task is "done" when it meets the Definition of Done below, not when the code
is written. Blocked work still lives in `new/` if it was never started, or in
`inprogress/` if it stalled partway; the `blocked_by:` field records what it is
waiting on.

## Creating a task

1. Copy `TASK_TEMPLATE.md` into `new/`.
2. Rename it to the naming convention below.
3. Fill in the front-matter and every section. Leave nothing blank — write
   "none" rather than omitting a section.

## Moving a task between statuses

A task moves between folders by **moving the file and editing its `status:`
field**. The two must always agree; a file whose `status:` disagrees with its
folder is a bug, and `tests/test_tasks.py` fails on it.

```bash
# move the file, then set status: inprogress and update updated:
mv new/TASK-20260910-004-example.md inprogress/
```

`tools/tasks.py` does both at once so they cannot drift:

```bash
python3 tools/tasks.py move TASK-20260910-004 inprogress
```

Any of the four statuses can be passed as the target, including `archive`:

```bash
python3 tools/tasks.py move TASK-20260910-004 archive
```

When the destination is `archive`, prefer the `archive` command — it takes the
reason as a required argument and writes it into the task's Completion summary
for you, so a called-off task never ends up without a record of why:

```bash
python3 tools/tasks.py archive TASK-20260910-004 "ถูกแทนที่ด้วย TASK-20260910-009"
```

The command moves the file to `archive/`, sets `status: archive`, and replaces
the `## Completion summary` body with `Archived <date> — <reason>`. An empty
reason is rejected and the task is left where it is.

Other commands:

```bash
python3 tools/tasks.py list      # all tasks by status, with [blocked] markers
python3 tools/tasks.py report    # counts + total estimated tokens
python3 tools/tasks.py new "Title"   # create from the template with the next id
```

## Required task file format

Every task is Markdown: YAML-ish front-matter, then fixed sections.

**Front-matter** (all keys required except `issue`, `prs`, `blocked_by`):

```yaml
---
id: TASK-YYYYMMDD-NNN     # unique; used by `move`
title: Short title
status: new               # new | inprogress | done — must match the folder
priority: normal          # low | normal | high
created: YYYY-MM-DD
updated: YYYY-MM-DD       # bump on every change
owner:                    # who is doing it (optional)
repo: ZyntroAI/fastapi-python-boilerplate
issue:                    # issue number, if any
prs: []                   # PR numbers — required for anything in done/
blocked_by:               # what it waits on, if anything
tokens: 0                 # estimated tokens, see below
---
```

**Sections** (in this order): Goal · Scope · Out of scope · Steps ·
Acceptance criteria · Dependencies / blockers · Files changed · Validation ·
Token usage · Notes · Completion summary.

See `new/example-task.md` for a filled-in example.

## Naming convention

```
<ID>-<slug>.md
```

- **ID** — `TASK-YYYYMMDD-NNN`, the creation date plus a per-day sequence, e.g.
  `TASK-20260910-001`.
- **slug** — the title, lowercased, spaces to `-`, ASCII only, ≤ 50 characters.
- Example: `TASK-20260910-001-issue63-pure-agent-dev.md`

`TASK_TEMPLATE.md` itself is the only file in this directory that does not
follow the convention.

## Definition of Done

A task may enter `done/` only when all of these hold:

1. Every item in **Steps** is complete, or its omission is explained in Notes.
2. Every **Acceptance criterion** is met and checked.
3. The **Validation** table is filled in with the actual commands run and their
   real results — not "should pass".
4. `prs:` lists the merged PR, or the task records the commit SHA. A task with
   no evidence does not go in `done/`.
5. `status: done` and the file is in `done/`.
6. Anything not finished is written in **Out of scope** or **Notes** — never
   left silently undone.

## Token usage

`tokens:` is an **estimate**, computed with this project's `len(text) // 4`
rule over the files a task lists. It is a size proxy for comparing tasks, not a
billing figure — real provider usage also includes the system prompt and the
context read into the session. The README says so plainly so nobody bills
against it.

## Validation

The structure is enforced, not trusted:

```bash
python3 -m pytest tests/          # from inside new.inprogress.done/
```

The tests fail when a task is missing a front-matter key, uses a duplicate
`id`, has a non-ISO date, disagrees with its own folder, or sits in `done/`
without a PR reference.

## Practical example

`new/example-task.md` is a real task in this repository: fixing the GitHub
Actions workflows, which currently fail at the *Set up job* step because
actions are referenced by tag instead of by pinned commit SHA. It is blocked on
write access to `.github/workflows/`, and it says so in `blocked_by:` — which is
why `tools/tasks.py list` prints it with a `[blocked]` marker.
