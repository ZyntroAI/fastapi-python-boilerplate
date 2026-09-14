#!/usr/bin/env node
// Tests for the AI Context engine. Node's built-in test runner — no deps.
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { match, best, assertContext } = require('../ai/context/matcher');
const { route, resolveLayers, needsApproval } = require('../ai/context/router');

const ROOT = path.join(__dirname, '..');
const REGISTRY = JSON.parse(fs.readFileSync(path.join(ROOT, 'registry.json'), 'utf8'));

test('context validation rejects malformed input', () => {
  assert.throws(() => assertContext(null), /plain object/);
  assert.throws(() => assertContext({}), /intent is required/);
  assert.throws(() => assertContext({ intent: '' }), /intent is required/);
  assert.throws(() => assertContext({ intent: 'x'.repeat(501) }), /exceeds 500/);
  assert.throws(() => assertContext({ intent: 'ok', targets: ['not-a-skill'] }), /unknown target/);
  assert.throws(() => assertContext({ intent: 'ok', keywords: 'nope' }), /keywords must be an array/);
  assert.throws(() => assertContext({ intent: 'ok', mutates: 'yes' }), /mutates must be a boolean/);
  assert.strictEqual(assertContext({ intent: 'deploy the build', mutates: true }), true);
});

test('deploy intent routes to vercel without a false "pr" hit', () => {
  const out = match({ intent: 'deploy the new build to preview and check status' });
  assert.ok(out.count > 0, 'expected at least one candidate');
  assert.strictEqual(out.candidates[0].skill, 'vercel');
});

test('exact target outranks plain keyword matches', () => {
  const out = match({ intent: 'do the thing', targets: ['jira'] });
  assert.strictEqual(out.candidates[0].skill, 'jira');
  assert.ok(out.candidates[0].reasons.includes('exact_target'));
});

test('keyword matching is word-bounded, not substring', () => {
  // "pr" must not fire on "preview"
  const out = match({ intent: 'show me the preview of the page' });
  const github = out.candidates.find((c) => c.skill === 'github');
  assert.ok(!github, 'github should not match on the word "preview"');
});

test('keywords from the context array are scored too', () => {
  const out = match({ intent: 'help me with this', keywords: ['discord'] });
  assert.strictEqual(out.candidates[0].skill, 'discord');
});

test('category contributes only a small weight', () => {
  const out = match({ intent: 'help', category: 'security' });
  const oauth = out.candidates.find((c) => c.skill === 'oauth');
  assert.ok(oauth && oauth.score === 10, `expected score 10, got ${oauth && oauth.score}`);
});

test('best() returns a single candidate and tolerates no match', () => {
  const one = best({ intent: 'send an email to the customer' });
  assert.ok(one && one.skill, 'expected a skill');
  const none = best({ intent: 'zzzz qqqq' });
  assert.strictEqual(none, null);
});

test('router refuses write skills without an approval grant', () => {
  const plan = route({ intent: 'deploy the build to vercel' });
  const step = plan.plan.find((s) => s.skill === 'vercel');
  assert.ok(step, 'vercel step missing');
  assert.strictEqual(step.approval_required, true);
  assert.strictEqual(step.runnable, false);
  assert.ok(step.missing_scopes.includes('deployment:write'));
});

test('router marks read-only skills runnable straight away', () => {
  const plan = route({ intent: 'look up the issue and summarize the sprint' });
  const jira = plan.plan.find((s) => s.skill === 'jira');
  assert.ok(jira);
  // jira declares issue:write so it still needs approval, but with the scope
  // granted and dry_run off it becomes runnable
  const withGrant = route({ intent: 'look up the issue in jira' }, {
    approved_scopes: jira.required_scopes,
    dry_run: false,
  });
  const step = withGrant.plan.find((s) => s.skill === 'jira');
  assert.strictEqual(step.missing_scopes.length, 0);
  assert.strictEqual(step.runnable, true);
});

test('progressive disclosure layers grow with context richness', () => {
  assert.deepStrictEqual(resolveLayers({ intent: 'x' }), ['core']);
  assert.deepStrictEqual(resolveLayers({ intent: 'x', targets: ['jira'] }), ['core', 'essential']);
  assert.deepStrictEqual(
    resolveLayers({ intent: 'x', targets: ['jira'], constraints: { requires_approval: true } }),
    ['core', 'essential', 'situational'],
  );
});

test('approval detection covers every mutating scope suffix', () => {
  assert.strictEqual(needsApproval(['table:read']), false);
  assert.strictEqual(needsApproval(['table:read', 'table:write']), true);
  assert.strictEqual(needsApproval(['email:send']), true);
  assert.strictEqual(needsApproval(['model:invoke']), true);
  assert.strictEqual(needsApproval(['cache:purge']), true);
  assert.strictEqual(needsApproval([]), false);
});

test('plan respects the limit option', () => {
  const plan = route({ intent: 'send an email and message slack about the deploy' }, { limit: 2 });
  assert.ok(plan.plan.length <= 2);
});

test('no secrets can leak through the engine surface', () => {
  const blob = JSON.stringify(REGISTRY);
  for (const bad of ['sk_live', 'sk_test', 'ghp_', 'AKIA', 'BEGIN PRIVATE KEY', 'xoxb-']) {
    assert.ok(!blob.includes(bad), `registry must not contain ${bad}`);
  }
  // schemas must never reference secrets by value, only by name
  const schema = fs.readFileSync(path.join(ROOT, 'skills', 'stripe-payments', 'schema.yaml'), 'utf8');
  assert.ok(schema.includes('credential_source'), 'schema should declare a credential source');
  assert.ok(!/sk_live|sk_test/.test(schema), 'schema must not embed a key');
});
