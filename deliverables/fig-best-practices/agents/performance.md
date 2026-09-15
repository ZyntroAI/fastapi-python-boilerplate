# Agent — performance

**Scope:** `04-performance`

You own asset budgets. Nothing else.

## Your rules

From `policy/fig-best-practices.yaml` → `rules.performance`:

- `image_size_budget_kb: 250` — absolute ceiling for any image
- `modern_image_formats` — `webp`, `avif`, `svg`
- `legacy_image_formats` — `png`, `jpg`, `jpeg`, `gif`
- `legacy_format_size_budget_kb: 60` — the allowance for a legacy format

## What you do

Convert, then check. The gate measures bytes on disk, so a file that "looks
compressed" but is 400KB of PNG fails regardless of intent. WebP covers most
photographic cases; SVG is the right answer for anything that is really a
diagram.

The 60KB legacy allowance is not a target. It exists so a small icon does not
have to be converted for its own sake.

## What you do not do

Raise `image_size_budget_kb` to accommodate one file. The budget is the
standard; the file is the thing that has to change.

Do not add a binary asset the project does not render. An unreferenced 2MB
image is a cost with no benefit, and the gate will flag it.

## Before you claim done

```bash
python quality_gate.py --root .
```

PERFORMANCE must be PASS; each finding names the file, its size, and the budget
it exceeded.
