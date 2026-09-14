# CWE-1321 Prototype Pollution Protection Suite

ID `TASK-SEC-CWE1321-001` · Priority P0 (Critical) · Assignee Dola AI Security Agent

Complete protection against **CWE-1321 (Prototype Pollution)**: detection rules
(JS/Python), sanitization logic, and integration points for the NotebookLM
Skill Suite and CI/CD. Rules live here under `deliverables/cwe1321-protection-suite/`.

## What this protects against

Prototype pollution lets an attacker inject keys such as `__proto__`,
`prototype`, or `constructor` into a payload so that the assignment/merge
mutates the shared prototype chain instead of a single object — often enabling
RCE, property injection, or auth bypass.

## Layout

```
deliverables/cwe1321-protection-suite/
├── js/
│   ├── eslint-rules.json          # ESLint: no-proto, no-prototype-builtins, detect-object-injection
│   ├── semgrep-cwe1321-js.yml     # Semgrep: __proto__ / prototype / constructor / naive merge
│   ├── codeql-query.ql            # CodeQL: writes to __proto__ / prototype / constructor
│   └── sanitize.js                # Runtime helpers: sanitizePrototypeKeys, safeMerge, safeClone, nullObject
├── python/
│   ├── bandit.config              # Bandit severity baseline for CI
│   ├── semgrep-cwe1321-py.yml     # Semgrep: setattr/dict/merge pollution patterns
│   └── safe_parser.py             # Runtime helpers: safe_load_json, safe_update_dict, fastapi_safe_dict
├── tests/
│   ├── test_safe_parser.py        # pytest (9 tests)
│   └── sanitize.test.mjs          # node --test (8 tests)
├── README.md
└── SKILL.md                       # Security Module: CWE-1321 (registry import doc)
```

## Usage

### JavaScript / TypeScript

```js
import { safeMerge, sanitizePrototypeKeys, nullObject } from './sanitize.js';

// JSON.parse yields an OWN __proto__ key — the realistic attack vector.
const attack = JSON.parse('{"__proto__":{"role":"admin"}}');
const safe = sanitizePrototypeKeys(attack); // __proto__ dropped
safeMerge(targetObj, attack);               // blocked key ignored

const map = nullObject();                    // no prototype at all
```

### Python / FastAPI / Pydantic

```python
from safe_parser import safe_load_json, safe_update_dict, fastapi_safe_dict

payload = safe_load_json(request.body)        # strips __proto__/prototype/constructor
safe_update_dict(model_dict, incoming, drop=True)  # raise with drop=False
clean = fastapi_safe_dict(raw_body)            # Pydantic/FastAPI-safe dict
```

## Detection rules

| Engine   | Rule set                                    | Scope |
|----------|---------------------------------------------|-------|
| ESLint   | `no-proto`, `no-prototype-builtins`, `security/detect-object-injection` | JS/TS |
| Semgrep  | `semgrep-cwe1321-js.yml`, `semgrep-cwe1321-py.yml` | JS/TS + Python |
| CodeQL   | `codeql-query.ql`                           | JS/TS data flow |
| Bandit   | `bandit.config` (severity baseline)         | Python |

## Skill integration

- `notebooklm-link-resolver` → filter query params for pollution keys.
- `artifact-router` → sanitize paths / IDs before use.
- `link-to-knowledge` → only accept safe payloads.
- `link-security` → remediation hook (safe loaders above).

## CI gate

`.github/workflows/cwe1321-protection-suite.yml` enforces the suite on every
change under this directory:

1. Parses every rule file — Semgrep YAML (JS + Python), `eslint-rules.json`,
   `manifest.json`, and `bandit.config` — and fails on anything malformed.
2. Runs the Python tests (`pytest tests/test_safe_parser.py`).
3. Runs the JS tests (`node --test tests/sanitize.test.mjs`).

All action refs are pinned to full commit SHAs and the workflow declares
`permissions: contents: read`.

## Verified

- Python: `9 passed` (pytest)
- JavaScript: `8 passed` (node --test)
- Output format matches suite standard: `{ status, keys, remediation }`.
