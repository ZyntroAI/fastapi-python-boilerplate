# 🏷️ Skill: Auto Label

**ติดป้าย PR อัตโนมัติจาก conventional-commit type + path ที่แตะ — เพิ่มเท่านั้น ไม่ลบป้ายคนอื่น**

Labels a pull request from two signals it already carries: the conventional-commit
type in the title, and the paths the diff touches. It only ever *adds* labels —
a human's label is never removed by a bot.

---

## Why it exists

`new-crystalcastle` carries malformed-YAML PRs, orphaned JSX, and drafts. The
cost of triage is not reading each PR — it is *routing* it: which of the 40
labels applies, so a reviewer can filter to `skills 🧠` or `security` and ignore
the rest. That decision is mechanical for the 80% of PRs that follow the repo's
own commit convention, and it is the part worth automating.

This skill automates the mechanical part and refuses the judgement part. A PR
that matches no rule gets no label and no guessing.

---

## When to use it

- A PR is opened or its title changes → classify and apply.
- Backfilling labels across existing PRs → `--dry-run` first, always.
- Auditing what *would* be labelled before turning the workflow on.

## When **not** to use it

- To decide mergeability, priority, or `ready-to-merge`. Labels here describe
  *what changed*, never *whether it is good*.
- To label issues. The rules read PR paths and commit types.

---

## The two signals

**1. Title (conventional commit).** The repo already enforces this format, so it
is free signal. `feat(docs): …` → `feature`, `docs`. `fix(skill:x): …` → `bugfix`,
`skills 🧠`.

**2. Changed paths.** `skills/**` → `skills 🧠`. `**/test_*.py` → `testing`.
`security/**` → `security`. `*.lock`, `requirements*.txt` → `dependencies`, `deps`.

Both signals combine. A `feat(security)` PR touching `security/cwe1321/` gets
`feature` + `security` — the intersection is the useful part.

---

## Rules

The rule table lives in `labels.json` and is data, not code. Each entry is
`{match, labels}` where `match` is either `title` (a commit type) or `paths`
(glob patterns). Edit the JSON to change behaviour; `classify.py` needs no edit.

Precedence is flat — every matching rule contributes. There is no first-match-wins
because "this PR is both docs and a skill" is true, and one of it being dropped
would be the bug.

---

## Safety

Three invariants the implementation holds:

1. **Additive only.** `apply_labels()` calls the add endpoint. It never calls
   remove, so a human's `ready-to-merge` survives a re-classification.
2. **No labels on no match.** An unmatched PR is returned with an empty set and
   the reason logged. Guessing a label is worse than an unlabelled PR.
3. **Dry-run is the default.** `apply.py` prints what it would do unless
   `--apply` is passed. Same convention as every other script in this repo.

---

## Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | This document |
| `classify.py` | Pure function: `(title, paths) -> set[label]` |
| `labels.json` | The rule table |
| `apply.py` | CLI: fetch a PR, classify, optionally apply |
| `tests/test_classify.py` | Runnable tests, no network |

---

## Usage

```bash
# what labels would PR #293 get?
python skills/auto-label/apply.py --repo ZyntroAI/fastapi-python-boilerplate --pr 293

# actually apply them
python skills/auto-label/apply.py --repo ZyntroAI/fastapi-python-boilerplate --pr 293 --apply

# classify from raw inputs, no network
python skills/auto-label/classify.py \
  --title "feat(docs): convert FIG_V4 into docs/fig" \
  --path docs/fig/README.md --path docs/fig/config/roles.json
```

```python
from classify import classify
classify("fix(skill:auto-label): handle missing path", ["skills/auto-label/classify.py"])
# -> {"bugfix", "skills 🧠"}
```

---

## Gotchas

- **Label names carry emoji.** `skills 🧠` and `docs 📝` both exist *alongside*
  plain `docs`. The rule table targets the exact string. Adding a label that
  does not exist creates it silently — check `labels.json` against
  `gh label list` if a label looks orphaned.
- **`docs 📝` vs `docs`.** Both exist. The table uses plain `docs` for the
  category and this is deliberate — see `labels.json` `_notes`.
- **Squash-merge titles.** The title the bot reads is the PR title, which becomes
  the squash subject. Fix the title before classifying, not after.
- **Fork PRs.** Read-only by default; classification works, applying may not.
