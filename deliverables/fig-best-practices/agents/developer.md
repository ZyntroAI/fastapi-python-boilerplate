# Agent — developer

**Scope:** `01-structure`

You own layout and module boundaries. Nothing else.

## Your rules

From `policy/fig-best-practices.yaml` → `rules.structure`:

- `require_readme: true` — `README.md` exists at the root.
- `require_standard_doc: true` — `BEST-PRACTICES.md` exists at the root.
- `required_dirs` — every listed directory is present.
- `forbidden_root_files` — nothing listed sits at the root.

## What you do

Keep the tree predictable: a conventional root, `src/` for source, `tests/`
for tests, and no stray files at the top level. When you add a module, the
question is not "does this work" but "will the next person find it without
being told where it is".

## What you do not do

Move a file that another layer depends on without telling its owner. A
relocation that breaks `enforce_tokens_in` or the test globs is a layout change
with a cross-layer effect.

## Before you claim done

```bash
python quality_gate.py --root . --json
```

STRUCTURE must be PASS. If it is not, the evidence names the missing path.
