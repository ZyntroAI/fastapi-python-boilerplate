/**
 * sanitize.js — CWE-1321 Prototype Pollution safe utilities.
 *
 * Detection rules (ESLint / Semgrep / CodeQL) flag the vulnerability; these
 * helpers are the runtime remediation. They are intentionally dependency-free
 * (no lodash `merge`, no `Object.assign` onto plain objects from untrusted
 * input) and exportable as ES modules.
 *
 * Risk keys that, if copied during a merge/assign, mutate the shared prototype
 * chain (Object.prototype / Function.prototype) rather than the target object.
 */
const BLOCKED_KEYS = Object.freeze(['__proto__', 'prototype', 'constructor']);

/**
 * Is the key unsafe to assign/copy?
 * @param {string} key
 * @returns {boolean}
 */
export function isBlockedKey(key) {
  return typeof key === 'string' && BLOCKED_KEYS.includes(key);
}

/**
 * Return an object with no prototype at all — safe to populate from untrusted
 * input because `obj.__proto__ = ...` is a plain own-property assignment that
 * cannot reach the shared Object.prototype.
 * @template T
 * @returns {T & object}
 */
export function nullObject() {
  return Object.create(null);
}

/**
 * Drop `__proto__`, `prototype`, `constructor` keys (any depth) from untrusted
 * JSON-like input before it is used to build objects. Returns a structurally
 * identical, pollution-free deep copy.
 *
 * @param {unknown} value
 * @returns {unknown}
 */
export function sanitizePrototypeKeys(value) {
  if (Array.isArray(value)) {
    return value.map(sanitizePrototypeKeys);
  }
  if (value !== null && typeof value === 'object') {
    const out = Object.create(null);
    for (const key of Object.keys(value)) {
      if (!isBlockedKey(key)) {
        out[key] = sanitizePrototypeKeys(value[key]);
      }
    }
    return out;
  }
  return value;
}

/**
 * Deep-merge `source` into `target`, refusing to copy blocked keys at every
 * level. Never merges into the target's prototype. Safer than lodash `merge`
 * / `Object.assign` for untrusted payloads.
 *
 * @template {{}} T
 * @param {T} target
 * @param {unknown} source
 * @param {{throwOnBlocked?: boolean}} [opts]
 * @returns {T}
 */
export function safeMerge(target, source, opts = {}) {
  const { throwOnBlocked = false } = opts;
  if (source === null || typeof source !== 'object' || Array.isArray(source)) {
    return target;
  }
  for (const key of Object.keys(source)) {
    if (isBlockedKey(key)) {
      if (throwOnBlocked) {
        throw new Error(`safeMerge: blocked prototype-polluting key '${key}'`);
      }
      continue; // drop by default
    }
    const srcVal = source[key];
    const tgtVal = target[key];
    if (
      srcVal !== null &&
      typeof srcVal === 'object' &&
      !Array.isArray(srcVal) &&
      tgtVal !== null &&
      typeof tgtVal === 'object' &&
      !Array.isArray(tgtVal)
    ) {
      safeMerge(tgtVal, srcVal, opts);
    } else {
      target[key] = sanitizePrototypeKeys(srcVal);
    }
  }
  return target;
}

/**
 * Deep-clone untrusted data with blocked keys stripped — a safe default
 * factory for the artifacts handled by link-security / artifact-router.
 * @param {unknown} input
 * @returns {unknown}
 */
export function safeClone(input) {
  return sanitizePrototypeKeys(input);
}

/** Standard remediation-report shape shared across the suite. */
export function report({ status = 'ok', keys = [], remediation = '' } = {}) {
  return { status, keys, remediation };
}

export { BLOCKED_KEYS };
export default { isBlockedKey, nullObject, sanitizePrototypeKeys, safeMerge, safeClone, report };
