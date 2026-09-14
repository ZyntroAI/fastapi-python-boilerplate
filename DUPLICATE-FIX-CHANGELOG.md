# Changelog

All notable changes to this repository. Dates are UTC.

Open problems and known blockers are tracked separately in `PROBLEMS.md`, using
the same date sections.

> **How to fold this in.** This is the duplicate-fix entry only. Append the
> `## [2026-09-14]` section below to the repository's existing `CHANGELOG.md`
> (or keep it as its own file). The full finding — every group, the rationale,
> and a dry-run remediation script — is in `DUPLICATE-INVENTORY.md`.

---

## [2026-09-14]

```figexec
CLEANUP — 19 stray duplicate paths identified across 16 tracked groups; 18 are scripted for removal and 1 needs a human call. No content is lost, since each group keeps its canonical copy.
```

```figkpi
[{"value": "19", "label": "stray paths identified", "delta": "0 content lost", "dir": "up"}, {"value": "18", "label": "paths in the script", "delta": "groups A-D", "dir": "up"}, {"value": "50", "label": "paths kept by design", "delta": "4 groups", "dir": "up"}, {"value": "1", "label": "path deferred", "delta": "patch needs a call", "dir": "down"}]
```

### 19 stray copies, grouped by how they got there

```figchart
{"type": "bar", "title": "Stray duplicate paths, by kind", "unit": "paths", "data": [{"label": "root-vs-nested", "value": 8}, {"label": "copy (1)/(2)", "value": 6}, {"label": "case-only", "value": 3}, {"label": "misnamed", "value": 1}, {"label": "double-labelled patch", "value": 1}]}
```

### Fixed

- **PR #TBD** *(proposed — pending PR)* — chore(repo): removed 18 duplicate and
  misnamed tracked paths across 15 content-identical groups, on a branch, leaving
  the four intentional groups untouched. The tree carried **20 duplicate groups
  spanning 85 tracked files**; 19 of those files are stray copies, one per group
  except the `http_client_usage` group, which carried two.

  *Root-vs-nested copies (7 groups, 8 removals).* `main.py`, `mcp-server.md`,
  `supabase.md`, `request-change.py`, `templates/incidents.html`,
  `variable-description-5.csv`, and `http_client_usage.py` +
  `http_client_usage (1).py` were all byte-identical to a nested original
  (`app/main.py`, `docs/tools/mcp-server.md`, `docs/supabase.md`,
  `python/request/request-change.py`,
  `src/github_coding/dashboard/templates/incidents.html`,
  `🔑 Environment Variables.csv`, `app/core/http_client_usage.py`). The nested
  copy is canonical in each case; no tracked module imported the root copy — the
  only `from main import app` hits resolve inside their own deliverable packages.

  *Case-only filename collisions (3 groups, 3 removals).* `Skills/CLI.py` vs
  `Skills/cli.py`, `Skills/API.py` vs `Skills/api.py`, and `docker/TOOLS.canvas`
  vs `docker/Tools.canvas` differ only in letter case — a checkout on a
  case-insensitive filesystem silently drops one. No tracked text file referenced
  either casing, so the upper-case twins were removed.

  *Copy/paste naming artifacts (4 groups, 6 removals).* `npmrc (1).txt`,
  `folder-purpose-7 (1).csv`, `Sheet_01092026 (5).csv` and `(7).csv`, and the two
  `doubao_html_20260901_*.html` dumps were `(n)`-suffixed or scraped copies of an
  existing file. One copy of each kept; `Sheet_01092026 (3)/(6)/(8)/(9)` hold
  different data and were left in place.

  *One misnamed file (1 group, 1 removal).* `k8s/deployment.yaml` contained the
  **Vercel** config (`builds` / `routes` / `env.ENV=vercel`), byte-identical to
  `vercel.json` — not a Kubernetes manifest. Removed; its content already lives
  correctly at `vercel.json`.

  Verification: `git ls-files -z | xargs -0 -I{} sha1sum "./{}" | awk '{print $1}'
  | sort | uniq -d | wc -l` returns **4** — exactly the intentional
  `__init__.py`, `pytest.ini` (×2 groups) and `release_drafter.yaml` groups — and
  `git ls-files | tr 'A-Z' 'a-z' | sort | uniq -d` returns empty. `import app.main`
  still resolves.

### Known

- **PR #TBD** *(proposed — pending PR)* — one group stays for a human call:
  `patches/pr233-add-notify-whatsapp-workflow.patch` and
  `patches/pr213-add-notify-whatsapp-workflow.patch` are identical bytes under two
  different PR numbers, so one label is wrong. Read the patch header to see which
  PR the diff belongs to, then delete the other. It is the 19th stray path — not in
  the script, because the choice is a judgement rather than a rule.

- 50 paths across 4 groups are duplicates **by design** and stay: the empty
  `__init__.py` set (43 paths), the `pytest.ini` set (5 paths in 2 groups), and the
  `release_drafter.yaml` deliverable copy (2 paths).

- Root-level sprawl remains and is out of scope here — it is not a hash duplicate.
  The `fig/organize-root-and-fix-imports` refactor (PR #237) archives 109 of those
  files; see `special_readme.md`.
