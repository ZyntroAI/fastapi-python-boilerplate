# Duplicate Inventory — `ZyntroAI/fastapi-python-boilerplate`

**Date:** 2026-09-14 (UTC)
**Method:** sha1 content hash over every tracked file (`git ls-files`), grouped by
identical hash; plus a case-insensitive filename-collision pass.
**Scope:** the whole tracked tree on `main`.
**Companion:** `DUPLICATE-FIX-CHANGELOG.md` — the repo-format changelog entry for
this cleanup.

```figexec
DUPLICATE AUDIT — 20 content-identical groups span 85 tracked paths; 19 of them are stray copies that can go, the other 50 are duplicates by design.
```

```figkpi
[{"value": "20", "label": "duplicate groups", "delta": "85 tracked paths", "dir": "up"}, {"value": "19", "label": "stray paths removable", "delta": "0 content lost", "dir": "up"}, {"value": "50", "label": "paths kept by design", "delta": "4 groups", "dir": "up"}, {"value": "1", "label": "group deferred", "delta": "needs a human call", "dir": "down"}]
```

## Nineteen stray copies, split five ways

The 20 identical-content groups divide cleanly: **16 are actionable** and **4 are
intentional**. The 16 actionable groups hold **19 stray copies**, not 16, because
one group (`http_client_usage`) carries three copies rather than two. Of the 16,
**15 are in the remediation script** — accounting for 18 removals — and **1
(group E) is deferred** with a single path, needing a human call. That is the
18 + 1 = 19.

```figchart
{"type": "bar", "title": "Stray duplicate paths, by kind (includes the deferred group E)", "unit": "paths", "data": [{"label": "root-vs-nested", "value": 8}, {"label": "copy (1)/(2)", "value": 6}, {"label": "case-only", "value": 3}, {"label": "misnamed", "value": 1}, {"label": "double-labelled patch", "value": 1}]}
```

The chart totals 19 stray paths across all five kinds. The script below removes
the first four kinds (18); kind E's single path is the deferred one.

The kinds in words:

- **A. Root-vs-nested copies** — the same file tracked twice, once at the repo root and once in the directory that owns it.
- **B. Case-only filename collisions** — two paths differing only in letter case. A real hazard: on macOS/Windows only one survives a checkout.
- **C. Copy/paste naming artifacts** — `name (1).ext`, `name (2).ext`…
- **D. Misnamed file** — `k8s/deployment.yaml` holds Vercel JSON, not a k8s manifest.
- **E. One file, two PR labels** — identical bytes filed under two PR numbers.

## A. Root-vs-nested copies — 7 groups, 8 removals

The nested path is canonical; the root copy is stray.

| Root copy (remove) | Canonical (keep) | Notes |
|---|---|---|
| `main.py` | `app/main.py` | No tracked `.py` imports the root copy. The only `from main import app` hits resolve inside their own deliverable packages. |
| `mcp-server.md` | `docs/tools/mcp-server.md` | Stale export of the docs file. |
| `supabase.md` | `docs/supabase.md` | Same. |
| `request-change.py` | `python/request/request-change.py` | Same. |
| `templates/incidents.html` | `src/github_coding/dashboard/templates/incidents.html` | The dashboard module owns its templates; root `templates/` is orphaned. |
| `variable-description-5.csv` | `🔑 Environment Variables.csv` | Identical bytes; the numbered name is a scratch export. |
| `http_client_usage.py` **and** `http_client_usage (1).py` | `app/core/http_client_usage.py` | The three-copy group — it contributes 2 removals, which is why 16 groups yield 19 paths. |

## B. Case-only filename collisions — 3 groups, 3 removals

| Remove | Keep | Hazard |
|---|---|---|
| `Skills/CLI.py` | `Skills/cli.py` | Only one survives on a case-insensitive filesystem; git shows both as tracked. |
| `Skills/API.py` | `Skills/api.py` | Same. |
| `docker/TOOLS.canvas` | `docker/Tools.canvas` | Same. |

No tracked text file references either casing, so removing the upper-case twins is safe.

## C. Copy/paste naming artifacts — 4 groups, 6 removals

| Remove | Keep | Notes |
|---|---|---|
| `npmrc (1).txt` | `npmrc.txt` | 38 B each. |
| `folder-purpose-7 (1).csv` | `folder-purpose-7.csv` | — |
| `Sheet_01092026 (5).csv`, `Sheet_01092026 (7).csv` | `Sheet_01092026 (4).csv` | Three identical sheets; siblings `(3)`, `(6)`, `(8)`, `(9)` hold different content and are **not** duplicates. |
| `doubao_html_20260901_030525.html`, `doubao_html_20260901_030619.html` | `app/pages/index.html` | Two scraped dumps identical to the app page — archive rather than delete if provenance matters. |

## D. Misnamed file — 1 group, 1 removal

`k8s/deployment.yaml` contains the **Vercel** config (`builds` / `routes` /
`env.ENV=vercel`), byte-identical to `vercel.json` — not a Kubernetes manifest.
Anyone reading `k8s/` is misled. Remove it; its content already lives correctly at
`vercel.json`.

## E. One file, two PR labels — 1 removal, needs a human call

`patches/pr233-add-notify-whatsapp-workflow.patch` and
`patches/pr213-add-notify-whatsapp-workflow.patch` are identical bytes under two
different PR numbers, so one label is wrong. Read the patch header to see which PR
the diff actually belongs to, then delete the other. It is the 19th stray path, but
**excluded from the script below** because the choice is a judgement, not a rule.

## Intentional — 50 paths in 4 groups, leave alone

These matched on content hash but are duplicates **by design**:

- **`__init__.py` — 43 paths in 1 group.** Empty package markers; the zero-byte file is required.
- **`pytest.ini` — 5 paths in 2 groups.** Identical config is intentional; centralise it later if it ever needs to change, not as a dedupe.
- **`release_drafter.yaml` — 2 paths in 1 group.** `.github/workflows/release_drafter.yaml` and the `deliverables/ci-workflow-sha-pin/fixed-workflows/` copy — the second is a **deliverable artifact**, a corrected copy kept beside its report.

43 + 5 + 2 = 50, across 1 + 2 + 1 = 4 groups.

## Related: root sprawl

Not a hash duplicate, but the same disease. The root carries exported CSVs, saved
HTML, web fonts, a zip, and scratch scripts. See `special_readme.md` — the
`fig/organize-root-and-fix-imports` refactor (PR #237) archives 109 of them.

## Remediation script

Runs against groups A–D — **18 removals**. **Dry-run by default**; pass `--apply`.
Each removal is a `git rm`, so every line is reversible from the commit it lands in.

```bash
#!/usr/bin/env bash
# dedupe.sh — remove the duplicate copies listed above (18 of the 19).
# The 19th is the patch group (E), left to a human. Usage:
#   ./dedupe.sh            # dry-run, prints what it would do
#   ./dedupe.sh --apply    # actually stage the removals
set -euo pipefail

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

run() {
  echo "  $*"
  [[ "$APPLY" == "1" ]] && "$@" || true
}

echo "Duplicate removals (apply=$APPLY):"

# A. root-vs-nested copies (8)
run git rm 'main.py'
run git rm 'mcp-server.md'
run git rm 'supabase.md'
run git rm 'request-change.py'
run git rm 'templates/incidents.html'
run git rm 'variable-description-5.csv'
run git rm 'http_client_usage.py'
run git rm 'http_client_usage (1).py'

# B. case-only collisions (3)
run git rm 'Skills/CLI.py'
run git rm 'Skills/API.py'
run git rm 'docker/TOOLS.canvas'

# C. (n) artifacts (6)
run git rm 'npmrc (1).txt'
run git rm 'folder-purpose-7 (1).csv'
run git rm 'Sheet_01092026 (5).csv'
run git rm 'Sheet_01092026 (7).csv'
run git rm 'doubao_html_20260901_030525.html'
run git rm 'doubao_html_20260901_030619.html'

# D. misnamed (1)
run git rm 'k8s/deployment.yaml'

echo
echo "Done. Review with:  git status && git diff --cached --stat"
[[ "$APPLY" == "0" ]] && echo "(dry-run — nothing was changed. Re-run with --apply.)" || true
```

## How to verify

```bash
# 1. remaining duplicate content-hash groups must be only the 4 intentional ones
git ls-files -z | xargs -0 -I{} sha1sum "./{}" | awk '{print $1}' | sort | uniq -d | wc -l
#   expect 4 (__init__.py, pytest.ini x2, release_drafter.yaml)

# 2. no two tracked paths differ only by case
git ls-files | tr 'A-Z' 'a-z' | sort | uniq -d          # empty

# 3. the entrypoint still resolves
python -c "import app.main"
```
