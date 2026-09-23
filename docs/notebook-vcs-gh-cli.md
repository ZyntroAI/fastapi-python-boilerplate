# Modern Notebook Version Control and GitHub CLI Integration Architectures

A working reference for teams that keep Jupyter notebooks in Git and automate them from the command line. It covers why notebooks diff badly, the tooling that fixes it, and how to wire the whole thing into CI with `gh` and GitHub Actions.

## 1. The Impedance Mismatch Between Jupyter Notebooks and Git

Interactive computing environments, notably Jupyter Notebooks (`.ipynb`), have become the standard interface for exploratory data science, machine learning research, and rapid prototyping. However, a fundamental structural friction exists between the operational model of distributed version control systems like Git and the underlying storage format of Jupyter Notebooks.

Git was designed primarily for line-oriented, plain-text source files where discrete line modifications correspond directly to logical semantic changes. In contrast, Jupyter Notebooks are structured JSON documents containing code cells, Markdown documentation, execution metadata, and embedded output artifacts.

When a developer executes a cell in a notebook without altering the underlying code, the notebook's internal state mutates. Execution counters increment, internal cell IDs update, and execution timestamps refresh. Furthermore, rich visual outputs — such as static plots, interactive JavaScript widgets, or HTML tables — are serialized directly into the JSON structure, frequently represented as massive base64-encoded strings. Standard Git line-based diff tools interpret these non-semantic metadata mutations and binary output shifts as hundreds or thousands of changed text lines.

The practical consequences:

- **Unreviewable diffs.** A one-character code change can produce a 40,000-line diff when a plot re-renders, burying the real change.
- **Merge conflicts that cannot be reasoned about.** Two people executing the same notebook produce conflicting `execution_count` values and cell IDs with no semantic disagreement underneath.
- **Repository bloat.** Base64 PNGs and HTML tables are stored in full on every commit that re-runs the notebook, and Git cannot delta-compress them well.
- **False signals in code review.** A reviewer cannot tell whether an output change reflects a logic change or merely a re-run.

Every tool in the rest of this document exists to close one of those four gaps.

## 2. Tooling Landscape

Four tools cover the space. They are complementary, not competing — most teams run two of them together.

### `nbstripout` — strip outputs and metadata before commit

`nbstripout` installs as a Git clean/smudge filter and rewrites notebooks in transit: outputs, `execution_count`, and volatile metadata are removed on the way into Git, and the working-tree file is left untouched.

```bash
pip install nbstripout
nbstripout --install            # writes filter.nbstripout + diff.ipynb to .git/config
nbstripout --install --attributes .gitattributes   # team-shared variant
```

The `--attributes` form is the one to prefer for a team: it records the filter in `.gitattributes` so every clone gets the same behaviour without each developer running the install step.

What it does **not** do: it does not strip cell IDs by default (those were added in nbformat 4.5 and are stable across runs, so this is usually correct), and it does not touch the code itself.

### `jupytext` — pair notebooks with a text representation

`jupytext` keeps a `.py` or `.md` file in sync with the `.ipynb`, so the thing under review is ordinary text.

```bash
pip install jupytext
jupytext --set-formats ipynb,py:percent notebook.ipynb   # create the paired .py
jupytext --sync notebook.ipynb                            # re-sync after editing either side
```

The `py:percent` format uses `# %%` cell markers and is the closest to a normal Python file, so it gets real syntax highlighting, real linting, and real diffs in review. The pairing is recorded in the notebook's own metadata, so `jupytext --sync` works without extra flags.

### `nbQA` — run standard linters and formatters on notebooks

`nbQA` lets `black`, `ruff`, `flake8`, `isort`, and `mypy` operate on notebooks by extracting the code cells, running the tool, and writing the result back.

```bash
pip install nbqa
nbqa ruff notebook.ipynb
nbqa black notebook.ipynb
nbqa mypy notebook.ipynb
```

This matters because a notebook that is never linted accumulates the same defects as unlinted Python — unused imports, shadowed names, mutable default arguments — but they hide inside JSON where no pre-commit hook looks.

### `papermill` — parameterised, reproducible execution

`papermill` executes a notebook end to end with injected parameters, which is what makes a notebook testable in CI.

```bash
pip install papermill
papermill input.ipynb output.ipynb -p start_date 2026-01-01 -p region apac
```

The input notebook declares its parameters in a cell tagged `parameters`; papermill overrides them at run time. The executed output notebook carries the results, and a non-zero exit code propagates if any cell raises.

## 3. Recommended Repository Layout

```
repo/
├── .gitattributes          # nbstripout filter registration
├── .pre-commit-config.yaml # nbstripout + nbQA hooks
├── notebooks/
│   ├── analysis.ipynb      # the notebook (outputs stripped on commit)
│   └── analysis.py         # jupytext pair, percent format — this is what gets reviewed
├── src/                    # importable logic lives here, not in cells
└── tests/
    └── test_notebooks.py   # papermill smoke run
```

The single most effective structural rule: **put reusable logic in `src/`, not in cells.** A notebook should orchestrate and display; anything that needs a unit test should be importable Python. This alone removes most of the diff pain, because the code under review stops living in JSON.

## 4. Wiring It Into Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: 0.8.1
    hooks:
      - id: nbstripout
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-ruff
        args: [--fix]
      - id: nbqa-black
```

Pin the `rev` to a tag, not a branch. An unpinned hook is a supply-chain dependency that changes under you.

## 5. GitHub CLI Integration

The `gh` CLI is what makes the notebook workflow scriptable. The commands below are the ones that come up repeatedly.

### Inspecting notebook history without cloning

```bash
# What changed in a notebook between two refs, as text
gh api repos/:owner/:repo/contents/notebooks/analysis.ipynb \
  -H "Accept: application/vnd.github.raw" -q '.content' | base64 -d | head -40

# The commit history for one notebook path
gh api "repos/:owner/:repo/commits?path=notebooks/analysis.ipynb" \
  --jq '.[] | "\(.sha[0:7])  \(.commit.author.date)  \(.commit.message | split("\n")[0])"'
```

### Opening a PR from a notebook change

```bash
git checkout -b analysis/q3-refresh
git add notebooks/analysis.ipynb notebooks/analysis.py
git commit -m "analysis: refresh Q3 notebook inputs"
git push -u origin analysis/q3-refresh
gh pr create --fill --base main
```

`--fill` takes the title and body from the commits. For a notebook PR the body should always state **whether outputs were regenerated**, because that is the one thing a reviewer cannot determine from the diff once `nbstripout` is in place.

### Reviewing a notebook PR from the terminal

```bash
gh pr diff 128 --patch | grep -E "^(\+\+\+|---)"        # which files moved
gh pr checkout 128 && jupytext --sync notebooks/analysis.ipynb
gh pr review 128 --comment -b "code cells look right; outputs not regenerated"
```

## 6. CI Automation with GitHub Actions

A notebook CI job has three concerns: lint the code, execute it, and fail loudly. Keep them as separate steps so a failure names its own cause.

```yaml
name: notebook-ci
on:
  pull_request:
    paths: ["notebooks/**", "src/**"]

permissions:
  contents: read

jobs:
  notebooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt nbqa papermill nbstripout
      - name: Lint notebook code
        run: nbqa ruff notebooks/
      - name: Verify outputs are stripped
        run: nbstripout --verify notebooks/*.ipynb
      - name: Execute notebooks
        run: |
          for nb in notebooks/*.ipynb; do
            papermill "$nb" "/tmp/$(basename "$nb")" --kernel python3
          done
```

Two details worth keeping:

- `nbstripout --verify` fails the build if a contributor committed outputs. Without it, the filter is advisory and someone will bypass it with `--no-verify`.
- `permissions: contents: read` is the whole job's privilege. A notebook CI run needs nothing more, and stating it explicitly is what keeps a compromised dependency from writing to the repo.

### Triggering it from `gh`

```bash
gh workflow run notebook-ci.yml --ref analysis/q3-refresh
gh run watch                      # follow the run live
gh run view --log-failed          # pull only the failing step's log
```

## 7. Failure Modes and Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Diff shows thousands of lines for a one-line change | Outputs or `execution_count` committed | Install `nbstripout` with `--attributes` |
| Merge conflict in `execution_count` / cell IDs | Both branches executed the same notebook | Strip metadata; treat the `.py` pair as the merge target |
| Repo size grows fast | Base64 images committed on every run | Strip outputs; store figures as separate files, not inline |
| `nbstripout --verify` passes locally, fails in CI | Filter installed in `.git/config` only, not `.gitattributes` | Re-install with `--attributes` and commit the file |
| `papermill` succeeds but produces empty output | Parameters cell not tagged `parameters` | Tag the cell; verify with `papermill --help` output listing the injected params |
| `nbqa mypy` reports import errors that do not occur in the notebook | Notebook relies on cells executed out of order | Move the logic into `src/` and import it |

## 8. Summary

- **The root problem** is that `.ipynb` is JSON carrying execution state and binary output, and Git diffs it line by line.
- **`nbstripout`** removes the noise at the source — install it with `--attributes` so it is shared, and verify it in CI.
- **`jupytext`** gives you a text file worth reviewing; the `.py` pair is the artifact under review, not the JSON.
- **`nbQA`** brings the ordinary Python toolchain to bear on notebook code.
- **`papermill`** turns a notebook into something CI can execute and fail on.
- **`gh` + Actions** close the loop: lint, verify, execute, and report — with `permissions: contents: read` and pinned action refs.
- **The structural rule that matters most:** logic in `src/`, notebooks for orchestration and display.
