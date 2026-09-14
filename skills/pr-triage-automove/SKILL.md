# 🧹 Skill: PR Triage Automove

**ย้ายไฟล์ที่อยู่ผิดที่ตอน PR triage — โดยที่แอป FastAPI ต้องบูตได้เสมอ**

A safeguard layer that runs *before* reviewers spend time on a cluttered PR. It
classifies root-level files, moves only the ones nothing depends on, and proves
the app still imports — or rolls the move back and says so.

This is the automated, CI-side form of `skills/organize-misplaced-files/`: same
three-condition gate, wrapped in a probe that makes it safe to run unattended.

---

## Why it exists

A repo root collects things. Workflow copies pulled in by mistake, exports,
fonts, saved HTML, one-off scripts. Reviewers can't tell the real tree from the
noise, and a cleanup PR is exactly where a needed config gets moved by accident.

The failure that motivates the import probe: `app/services/__init__.py` importing
a class that did not exist stopped the entire app from booting, and nothing in CI
noticed because the tests never got that far. A cleanup tool that cannot detect
that is worse than no tool.

---

## The gate — a file moves only when all three hold

| # | Condition | How it is checked |
| - | --------- | ----------------- |
| 1 | Not a canonical repo file or entrypoint | allow-list in `config.py` (`README.md`, `requirements.txt`, `main.py`, …) |
| 2 | No tracked `.py` imports it as a module | **AST parse**, top-level module name — never grep |
| 3 | Its name appears in no other tracked file | text scan of `.md`, `.yml`, `.yaml`, `.json`, `.toml`, `Makefile`, `Dockerfile*`, … |

Condition 2 is the one that needs parsing. Python 3 uses absolute imports, so
`import auth` inside `app/api/auth.py` resolves to *top-level* `auth` — root
`auth.py` — even though a sibling file of the same name exists next to it. Only
the import graph tells those apart. A file that fails to parse is reported
(`unparseable_py`) rather than silently treated as unused.

Condition 3 is what parks a root `deployment.yaml` named by
`k8s/kustomization.yaml`, or a `Plan` file named by `ROADMAP.md`. Those look like
clutter and are not.

---

## The import probe — what makes it safe unattended

```
classify  →  probe (before)  →  git mv  →  probe (after)  →  regression?
                                                              ├─ none  → keep
                                                              └─ found → roll back everything
```

The probe imports each entrypoint in a **child process** and records
`status:signature` — so a poisoned import cannot kill the triage run itself.

Regression rules, each earned in practice:

- **A FAIL that was already a FAIL is not a regression.** Most repos have
  something that does not import. Blocking on pre-existing breakage would make
  the skill unusable exactly where it is most needed. This is how your damage
  gets told apart from what was already broken.
- **UNKNOWN is never a regression.** It means the probe could not run — an
  environment fact, not evidence about the move.
- **FAIL → OK is a fix, not a regression.** Only a drop in rank blocks.

Entrypoints are discovered from how the repo is actually run — `uvicorn x:app`,
`gunicorn`, Vercel's `"module"`, plus `main` / `app.main` when present.

---

## Usage

```bash
# dry-run — prints the plan, touches nothing (this is the default)
python skills/pr-triage-automove/automove.py --repo .

# write the PR comment body
python skills/pr-triage-automove/automove.py --repo . --comment comment.md

# actually move, with rollback on regression
python skills/pr-triage-automove/automove.py --repo . --apply

# a back-dated archive folder
python skills/pr-triage-automove/automove.py --repo . --apply --stamp 2026-09
```

Exit codes: `0` fine · `2` a regression was found and the move rolled back.

Programmatic:

```python
from pr_triage_automove import automove
report = automove.run(repo, apply=False)       # dry-run dict
print(automove.render_comment(report))         # the PR body
```

---

## Configuration

Drop a `.pr-triage-automove.json` at the repo root; it merges over the defaults:

```json
{
  "canonical": ["README.md", "requirements.txt", "main.py", "my-custom-config.toml"],
  "probe_targets": ["app.main", "main"],
  "archive_dir": "archive/root-2026-09",
  "max_move": 200
}
```

| Key | Default | Meaning |
| --- | ------- | ------- |
| `canonical` | built-in list | files that are never candidates |
| `probe_targets` | `[]` → auto-detect | entrypoints to import-check |
| `archive_dir` | `archive/root-<YYYY-MM>` | destination root |
| `max_move` | `500` | refuse to move more than this in one run |
| `reference_suffixes` | built-in list | file types scanned for references |
| `archive_layout` | built-in map | suffix → subfolder |

Malformed JSON falls back to defaults rather than erroring — a broken config
file must not be able to disable the safety gate.

---

## CI integration

The workflow lives at `examples/pr-triage-automove.yml` in this folder, not in
`.github/workflows/`, on purpose: pushing there needs the `workflows` permission,
which automation tokens often lack. Copy it in with elevated rights when you are
ready.

It is **report-only by default** — the job prints the diff comment and fails
nothing. Auto-moving in CI (adding `--apply` and committing the result back) is a
deliberate opt-in, because a bot that relocates files on every PR is a policy
decision, not a lint rule.

Two safety properties the workflow relies on:

- the job runs with `permissions: contents: read, pull-requests: write` — the
  move is computed, never pushed by default;
- `--report` and `--comment` are written as artifacts even when the run fails, so
  the evidence survives a red job.

---

## Layout

```
skills/pr-triage-automove/
├── SKILL.md                 # this file
├── __init__.py              # package exports
├── config.py                # canonical list, layout, overlay loading
├── classify.py              # AST classification + reference scan
├── probe.py                 # import-health probe + regression rules
├── automove.py              # orchestrator + rollback + comment rendering
├── examples/
│   └── pr-triage-automove.yml
└── tests/
    ├── conftest.py          # imports the hyphenated dir as a package
    ├── test_automove.py     # end-to-end against throwaway git repos
    └── test_unit.py         # pure decision logic
```

```bash
python -m pytest skills/pr-triage-automove/tests -q
```

---

## Gotchas

- **`git mv`, never `mv`.** History and rename detection in the PR diff depend
  on it. For a path starting with `-`, terminate options: `git mv -- "- x.txt" dest/`.
- **Nothing is ever deleted.** A bot that deletes files during triage is a worse
  problem than a cluttered root. Everything lands in `archive/`.
- **Basename matching must be exact-enough.** A root file named `Plan` is matched
  as `Plan`; the scan errs toward *holding* a file, which costs a human glance,
  versus moving something needed, which costs a broken build.
- **The probe is per-repo-configurable.** If your entrypoint is not in
  `Dockerfile` / `vercel.json` / `Makefile`, set `probe_targets` — auto-detection
  cannot guess a custom runner.
- **Re-verify after writing.** Some environments reset files mid-task; confirm a
  config or file edit landed before running the tool.
