# SPECIAL README — the Refactor

**Scope:** branch `fig/organize-root-and-fix-imports` (head `8bc19ee`), PR
[#237](https://github.com/ZyntroAI/fastapi-python-boilerplate/pull/237), against
`main`. Two commits do the work — `c161511` *docs: rewrite README to match the
repository as it stands* and `8bc19ee` *chore: archive misplaced root files and
repair the FastAPI import chain*.
**Size:** 118 files changed, +668 / −86.

```figexec
REFACTOR SHIPPED — 109 misplaced root files archived with zero deletions (every move a 100% rename), and the FastAPI import chain repaired so `from app.services.*` resolves again.
```

```figkpi
[{"value": "109", "label": "files archived", "delta": "0 deleted", "dir": "up"}, {"value": "118", "label": "files changed", "delta": "+668 / −86", "dir": "up"}, {"value": "2", "label": "import-chain fixes", "delta": "services + config", "dir": "up"}, {"value": "4", "label": "root files left for a human call", "delta": "still referenced", "dir": "up"}]
```

## The root had become a dumping ground

The repository root carried exported CSVs, saved HTML pages, web fonts, one-off
scripts, chat transcripts and pulled-in workflow copies, all sitting beside the
real tree. Commit `8bc19ee` moved **109** of those files into
`archive/root-2026-09/`, leaving the root legible again.

```figchart
{"type": "bar", "title": "Files archived, by destination folder", "unit": "files", "data": [{"label": "exports", "value": 43}, {"label": "assets", "value": 22}, {"label": "scripts", "value": 17}, {"label": "notes", "value": 8}, {"label": "misc", "value": 8}, {"label": "html", "value": 7}, {"label": "manifests", "value": 4}]}
```

The layout is deliberate, not a single heap:

| Folder | Holds |
|---|---|
| `exports/` | CSV and TXT exports, patch files, shell snippets |
| `assets/` | Fonts (`.woff2`), images, zip archives |
| `scripts/` | One-off root `.py` scripts nothing imported |
| `notes/` | Root markdown notes and chat exports |
| `html/` | Saved HTML pages |
| `manifests/` | Root YAML that belongs in `.github/workflows/` or `k8s/` |
| `misc/` | Everything else |

## The break was two lines in the service package

The refactor is not only tidying — it repairs a genuine outage.
`app/services/__init__.py` did `from .users import UserService`. No class by that
name has ever existed in that package (`users.py` defines `UserRepo`, `get_repo`,
`fanout_profile`). A package `__init__` runs **before** any submodule import, so
that one wrong name made every `from app.services.<x> import y` raise — which in
turn stopped `app.main`, the entrypoint in `app/Dockerfile`, from importing at all.

The fix removes the phantom imports and documents the policy of importing nothing
at package-import time, mirroring `app/__init__.py`.

`app/core/config.py` needed the same class of repair for a different reason: it
was written against Pydantic's legacy inner-class `Config` and relied on v2's
`extra="forbid"` default. The repo `.env` carries keys the app does not declare
(BytePlus, WhatsApp Cloud API, …), so the app refused to start whenever those were
present. It now uses `SettingsConfigDict(env_file=".env", extra="ignore")`.

## Nothing was deleted — every file is one `git mv` from coming back

That is the safety property that makes this refactor reviewable. Each archived file
is still on disk and in history; only its path changed. Restore any one:

```bash
git mv archive/root-2026-09/<subdir>/<file> <original-path>
```

A restore round-trip is part of the verification below, so the claim is checkable,
not merely asserted.

## A file moved only when three gates held

`scripts/move_root_clutter.py` decided the moves, and the rule is strict enough to
trust:

1. It is not a canonical repo file (`README.md`, `package.json`, `requirements.txt`, …).
2. No tracked Python file imports it as a module — **AST-verified, not grep**.
3. Its basename appears in no other tracked file — no doc, workflow, Makefile or manifest still points at it.

Gate 2 is why the result is safe; gate 3 is why it is useful, and it is why some
root files stayed. Several only *look* like clutter: `ci.yml`, `codeql.yml` and
`deployment.yaml` are still referenced by `FILE-MANIFEST.md`, `k8s/README.md` and
`k8s/kustomization.yaml`; `Plan` is referenced by `ROADMAP.md`;
`context_guard_4060.py` by `app/core/context_guard.md`; the root `*.py` scripts are
named in `Skills/Readme.md`. Retire those references and the files can follow them
into the archive.

## Four root files still need a human call, not a script

These were left in place because something still points at them:

- **`.env`** — tracked in git and carrying real keys. Already flagged in the README; this is the one to act on first.
- **`Dockerfile.txt`** — a Dockerfile stored with a `.txt` extension; referenced by `README.md`.
- **`gitignore`** — a duplicate of `.gitignore` (no dot), referenced by `CHANGELOG.md`. Fix the reference, then remove the file.
- **`index.html` / `md009.md` / `md032.md`** — referenced by `pytest/README.md` and `.vscode/package.json`.

## Also on this branch

- **`pyproject.toml`** — the dependency and tooling declaration the branch was missing.
- **`requirements.txt`** — pinned runtime dependencies.
- **`skills/organize-misplaced-files/SKILL.md`** — the repeatable version of this cleanup.
- **`skills/pr-full-lifecycle/SKILL.md`** — branch → PR → CI → merge, end to end.
- **`.gitignore`** — adds `.gatevenv/`, the local virtualenv the import-health check creates.
- **`README.md`** — rewritten to match the repository as it actually stands.

## How to verify

```bash
git checkout fig/organize-root-and-fix-imports

# 1. the import chain this branch repairs
python -c "import app.services"          # was failing on `from .users import UserService`
pip install -r requirements.txt -q       # then: python -c "import app.main"

# 2. lossless: every root deletion is a 100% rename, so no file is truly gone
git diff --name-status -M --find-renames=100% origin/main...HEAD | \
  awk '{print $1}' | cut -c1 | sort | uniq -c
#   expect 109 R, 4 A, 0 D — no deletions at all

# 3. the archive is complete — every archived path still resolves
git ls-tree -r --name-only HEAD archive/root-2026-09/ | while read -r f; do
  git cat-file -e "HEAD:$f" || echo "MISSING $f"
done                                     # prints nothing

# 4. a restore round-trip on one file
git mv archive/root-2026-09/scripts/request-change.py ./request-change.py
git mv ./request-change.py archive/root-2026-09/scripts/request-change.py
```

## Where this leads next

`DUPLICATE-INVENTORY.md` and its `DUPLICATE-FIX-CHANGELOG.md` entry ship on this
same branch. They document the same disease caught earlier: 19 stray paths in 16
content-identical groups (`main.py` vs `app/main.py`, case-only collisions,
`name (1).csv` artifacts, and `k8s/deployment.yaml` holding Vercel JSON). The
inventory's script is dry-run by default and **is not applied here** — the three
docs land as separate commits on one branch so each stays reviewable on its own.
