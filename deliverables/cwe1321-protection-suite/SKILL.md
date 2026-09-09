# Security Module: CWE-1321 — Prototype Pollution Protection

**ID:** `cwe1321-protection-suite-v1.0.0`  **Version:** 1.0.0  **Type:** Security Module
**Tags:** cwe-1321, prototype-pollution, security, semgrep, bandit, eslint, codeql, sanitizer
**Severity:** P0 (Critical)  **Visibility:** Public · Production Ready

## Overview

Detection rules (ESLint / Semgrep / CodeQL / Bandit) plus runtime sanitization
helpers (JS + Python) that together eliminate **CWE-1321 Prototype Pollution**
from the NotebookLM Skill Suite and any FastAPI/JS code paths that ingest
untrusted JSON.

## Files (in `deliverables/cwe1321-protection-suite/`)

```
js/sanitize.js          runtime helpers (sanitizePrototypeKeys, safeMerge, safeClone, nullObject)
js/eslint-rules.json    no-proto / no-prototype-builtins / detect-object-injection
js/semgrep-cwe1321-js.yml
js/codeql-query.ql
python/safe_parser.py   safe_load_json / safe_update_dict / fastapi_safe_dict
python/bandit.config
python/semgrep-cwe1321-py.yml
tests/                  8 JS tests (node --test) + 9 Python tests (pytest)
```

## Threat model (CWE-1321)

Untrusted input carrying `__proto__`, `prototype`, or `constructor` keys can,
when merged/assigned onto an object or mapped onto attributes by a framework
(Pydantic coercion, ORM `**kwargs`, `setattr`), mutate shared prototype / class
state. This often escalates to RCE or auth bypass.

## Protection gates

| Layer      | Engine   | What it enforces |
|------------|----------|------------------|
| Static JS  | ESLint   | `no-proto`, `no-prototype-builtins`, `security/detect-object-injection` |
| Static JS  | Semgrep  | `__proto__`/`prototype`/`constructor` writes, naive merge |
| Data-flow  | CodeQL   | writes to `__proto__`/`prototype`/`constructor` |
| Static Py  | Semgrep  | setattr / dict / merge pollution patterns |
| Static Py  | Bandit   | severity baseline (medium+) |
| Runtime    | JS/Python helpers | strip blocked keys at every depth, safe merge, safe loaders |

## Verification gates (Gate 5 of skill template)

1. **Structure valid** — YAML/JSON rules parse; helpers are dependency-free.
2. **Vuln scan** — Semgrep + Bandit flag the target patterns in real payloads.
3. **Permission check** — safe loaders never write outside the target object.
4. **Output verify** — report shape is the suite standard `{status, keys, remediation}`.

## Skill wiring

- `notebooklm-link-resolver` → run query params through `sanitizePrototypeKeys`.
- `artifact-router` → sanitize paths / IDs via `safe_parser.strip_blocked_keys`.
- `link-to-knowledge` → accept only payloads that pass `fastapi_safe_dict`.
- `link-security` → remediation hook (safe loaders).

## Import

Place under `skills/` (registry) or keep in `deliverables/cwe1321-protection-suite/` as the source
of truth. Both copies are kept in sync. Register in `skills/index.json` with
`provides: ["cwe-1321-protection", "prototype-pollution-detection", "prototype-pollution-sanitization"]`.
