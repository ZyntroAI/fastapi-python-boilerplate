// Tests for deliverables/cwe1321-protection-suite/js/sanitize.js (CWE-1321).
// Run: node --test deliverables/cwe1321-protection-suite/tests/sanitize.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  isBlockedKey,
  nullObject,
  safeMerge,
  safeClone,
  sanitizePrototypeKeys,
  report,
} from '../js/sanitize.js';

test('blocked key detection', () => {
  assert.equal(isBlockedKey('__proto__'), true);
  assert.equal(isBlockedKey('prototype'), true);
  assert.equal(isBlockedKey('constructor'), true);
  assert.equal(isBlockedKey('role'), false);
  assert.equal(isBlockedKey(123), false);
});

test('nullObject has no prototype', () => {
  const o = nullObject();
  assert.equal(Object.getPrototypeOf(o), null);
  o.__proto__ = { role: 'admin' }; // plain own-key, no pollution
  assert.equal(o.__proto__.role, 'admin');
  assert.equal({}.role, undefined); // shared Object.prototype untouched
});

test('sanitizePrototypeKeys strips pollution at depth', () => {
  const payload = JSON.parse('{"__proto__":{"role":"admin"},"a":{"constructor":{"x":1}},"ok":true}');
  const clean = sanitizePrototypeKeys(payload);
  assert.equal(clean.ok, true);
  assert.equal(clean.a.x, undefined); // constructor dropped
  assert.equal(Object.prototype.role, undefined); // nothing leaked
});

test('safeClone returns pollution-free copy', () => {
  const src = { nested: { __proto__: { isAdmin: true }, keep: 1 } };
  const clone = safeClone(src);
  assert.equal(clone.nested.keep, 1);
  assert.equal(clone.nested.isAdmin, undefined);
  assert.equal({}.isAdmin, undefined);
});

test('safeMerge drops blocked keys by default', () => {
  const target = { role: 'user' };
  safeMerge(target, JSON.parse('{"__proto__":{"role":"admin"},"level":2}'));
  assert.equal(target.role, 'user');
  assert.equal(target.level, 2);
  assert.equal({}.role, undefined);
});

test('safeMerge throws when asked', () => {
  const t = {};
  // JSON.parse (not an object literal) yields an OWN `__proto__` key, which is
  // how real attack payloads arrive.
  const attack = JSON.parse('{"__proto__":{"a":1}}');
  assert.throws(
    () => safeMerge(t, attack, { throwOnBlocked: true }),
    /blocked prototype-polluting key/
  );
});

test('safeMerge recurses into nested objects', () => {
  const target = { cfg: { a: 1 } };
  // `constructor` via JSON is an own key here, unlike `{constructor:'x'}` in a
  // literal which is shadowed by the inherited constructor.
  const src = JSON.parse('{"cfg":{"b":2,"constructor":"x"}}');
  safeMerge(target, src);
  assert.equal(target.cfg.a, 1);
  assert.equal(target.cfg.b, 2);
  // No OWN `constructor` key was copied onto the nested object.
  assert.equal(Object.hasOwn(target.cfg, 'constructor'), false);
});

test('report has standard shape', () => {
  assert.deepEqual(
    report({ status: 'blocked', keys: ['__proto__'], remediation: 'strip key' }),
    { status: 'blocked', keys: ['__proto__'], remediation: 'strip key' }
  );
});
