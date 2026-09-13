# Archived root clutter — 2026-09

165 files sat at the repository root alongside the real tree: pulled-in workflow
copies, spreadsheet exports, font/binary assets, scratch notes, HTML dumps and
one-off scripts. 109 of them were moved here on 2026-09-13.

**Nothing was deleted.** Every file is still in git history and still on disk —
just no longer at the root. Restore any file with:

```bash
git mv archive/root-2026-09/<subdir>/<file> <original-path>
```

## Layout

| Folder | Contents |
| ------ | -------- |
| `scripts/` | One-off root-level `.py` scripts nothing imported |
| `manifests/` | `ci.yml`, `codeql.yml`, YAML copies that belong in `.github/workflows/` or `k8s/` |
| `exports/` | CSV / TXT exports, patch files, shell snippets |
| `html/` | Saved HTML pages |
| `assets/` | Fonts (`.woff2`), images, archives |
| `notes/` | Root-level markdown notes and chat exports |
| `misc/` | Everything else |

## Why these, and not others

A file was moved **only** when all three held (checked by
`scripts/move_root_clutter.py`):

1. it is not a canonical repo file (`README.md`, `package.json`, `requirements.txt`, …);
2. no tracked python file imports it as a module (AST-verified, not grep);
3. its basename appears in no other tracked file — no doc, workflow, Makefile or
   manifest still points at it.

54 root files were **kept** for that reason. Several look like clutter and are
not: `ci.yml`, `codeql.yml` and `deployment.yaml` are still referenced by
`FILE-MANIFEST.md`, `k8s/README.md` and `k8s/kustomization.yaml`; `Plan` is
referenced by `ROADMAP.md`; `context_guard_4060.py` is referenced by
`app/core/context_guard.md`; the several `*.py` scripts at root are named in
`Skills/Readme.md`.

If you later retire those references, the file can follow them here.

## Still worth a decision

These are at the root and were **not** moved because something still points at
them — they need a call, not a script:

- `.env` — tracked in git and carries real keys. Already flagged in the README.
- `Dockerfile.txt` — a Dockerfile stored as `.txt`; referenced by `README.md`.
- `gitignore` — a duplicate of `.gitignore` (no dot) referenced by `CHANGELOG.md`.
- `index.html` / `md009.md` / `md032.md` — referenced by `pytest/README.md` and `.vscode/package.json`.
