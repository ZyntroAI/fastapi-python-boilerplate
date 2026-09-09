# Test Report — CWE-1321 Prototype Pollution Protection Suite

**Task:** TASK-SEC-CWE1321-001 · **Date:** 2026-09-09 · **Status:** PASSING

## Summary

| Layer      | Suite        | Result | Duration |
|------------|--------------|--------|----------|
| JavaScript | `node --test deliverables/cwe1321-protection-suite/tests/sanitize.test.mjs` | 8 passed / 0 failed | ~65 ms |
| Python     | `pytest deliverables/cwe1321-protection-suite/tests/test_safe_parser.py`     | 9 passed / 0 failed | ~0.03 s |

Run in both `ZyntroAI/fastapi-python-boilerplate` and `ZyntroAI/new-crystalcastle`
(mirrored copy) — identical green result.

## Test cases (mapped from the task checklist)

### URL query-param sanitization
`https://notebooklm.google.com/path?__proto__=admin` → **Sanitized**: blocked key
dropped; helper returns a pollution-free object. JS `safeClone` / `sanitizePrototypeKeys`.

### JSON payload rejection
`{"__proto__":{"role":"admin"}}` → **Rejected / stripped**: `safe_load_json`,
`safeMerge(drop=True)`, `safe_update_dict(drop=True)` raise `ValueError`; the
polluting key never reaches `Object.prototype` / class state (asserted via
`{}.role === undefined` / `not hasattr(dict, "role")`).

### Merge blocking
`merge(safe, {__proto__: ...})` → **Blocked**: `safeMerge` ignores blocked keys by
default and throws with `{throwOnBlocked:true}`. `constructor`/`prototype` handled
identically.

### Output format
Remediation report matches the suite standard: `{ status, keys, remediation }`
(asserted in JS `report` + Python `report`).

## Edge cases verified

- Blocked-key detection accepts only the three reserved keys; benign keys pass.
- Nested / recursive payloads stripped at every depth (not just top level).
- `Object.create(null)` objects are safe to populate from untrusted input.
- JSON-derived payloads (real attack vector, own `__proto__` key) vs object
  literals (prototype-setter) — both handled.

## CI gate

`.github/workflows/security-scan.yml` (fastapi repo) runs Semgrep JS + Python
(`--error` on ERROR severity) plus Bandit on every PR; also re-runs the two
self-test suites so the runtime guards prove themselves in CI.
