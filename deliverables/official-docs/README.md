# Official Documentation — Registry, Components & Link Verification

Single source of truth for the official documentation links used across the
ZyntroAI FastAPI boilerplate, plus the two UI pieces that surface them: an
official-docs bar and an image gallery where every card links back to the
provider that produced the asset.

Version `1.2.0-origin` · links verified **2026-09-14**.

## Why this exists

The original link set (FastAPI · Python · FIG · Dola · ZyntroAI) contained six
URLs that do not resolve — a 404 path, a hostname that does not exist, and a
file that was never committed. Shipping them as "official references" would
have put dead links in the UI. Every URL here was checked with a live HTTP
request first, and the ones that failed are recorded in `CORRECTED_LINKS` with
their reason and replacement, so the audit trail survives the fix.

### Corrected links

| Cited | Problem | Now |
|-------|---------|-----|
| `fastapi.tiangolo.com/advanced/architecture/` | 404 — path does not exist | `fastapi.tiangolo.com/advanced/` |
| `docs.hellofig.ai/` | host does not resolve | `hellofig.app/` |
| `share.hellofig.app/help` | 404 — host serves shared conversations, not a help centre | `share.hellofig.app/` |
| `hellofig.app/changelog` | 404 — no public changelog at that path | removed |
| `hellofig.ai/` | different domain from the official platform site | `hellofig.app/` |
| `.../blob/Origin/.github/CHECKLIST_BILLING.md` | 404 — not present on `Origin` or `main` | removed |

## Layout

```
official-docs/
├── src/
│   ├── official-docs.js      # registry — the source of truth
│   ├── official_docs.py      # Python twin (backend + CI)
│   ├── official-docs.json    # generated mirror, read by Python
│   ├── utils.ts              # TypeScript helpers
│   ├── Company.jsx           # docs bar + image gallery
│   └── Company.module.css
├── scripts/
│   ├── export_registry.mjs   # JS registry -> JSON
│   ├── verify_links.py       # live HTTP check (CI gate)
│   └── render_smoke.mjs      # server-render smoke test
├── tests/
│   ├── official-docs.test.mjs
│   └── test_official_docs.py
└── SKILL.yaml
```

`official-docs.js` is authoritative. The JSON mirror is generated — never edit
it by hand — and a parity test fails if the two ever disagree.

## Usage

Front end:

```jsx
import Company, { OfficialDocsBar, UnifiedImageCard } from "./Company.jsx";
import { analyze, detectSource, getSourceDoc } from "./official-docs.js";

detectSource("https://dola.ai/x.png");   // "Dola"
analyze("https://hellofig.app/og.png");  // { source: "FIG", docRef: ..., isImage: true, ... }
```

Back end:

```python
from official_docs import load_registry, source_from_headers

registry = load_registry()
registry.primary_url("fastapi")          # "https://fastapi.tiangolo.com/"
source_from_headers(request.headers)     # "Dola" — from x-asset-source or Referer
```

The two languages run the same detection rules on different inputs: the browser
reads a `data-source` attribute off the image element, the server reads the
`x-asset-source` header and falls back to `Referer`.

Every registered URL is validated as `http`/`https` before it becomes an
`href`, so a `javascript:` or `data:` value can never reach the DOM.

## Tests

```bash
node scripts/export_registry.mjs      # regenerate the JSON mirror
node --test tests/                    # 13 JS tests
python -m pytest tests/ -q            # 23 Python tests
python scripts/verify_links.py        # live HTTP check of all 11 links
node scripts/render_smoke.mjs         # 11 render assertions
```

Needs `esbuild`, `react`, `react-dom` and `prop-types` for the render smoke
test only (`npm install --no-save`). Everything else is dependency-free —
the Python side is standard library only.

## CI gate

`verify_links.py` exits non-zero when any link stops resolving, so a dead
reference fails the build instead of reaching the UI:

```yaml
- name: Verify official documentation links
  run: python deliverables/official-docs/scripts/verify_links.py
```

## Adding a provider

1. Add the entry to `OFFICIAL_DOCS` in `src/official-docs.js` (name, label,
   source, links).
2. Map the detected source name in `SOURCE_KEYS`.
3. Extend `detectSource()` (both languages) if the host needed.
4. Re-run `export_registry.mjs`, then the tests and `verify_links.py`.

`tests/test_official_docs.py::ParityTest` guards the drift.
