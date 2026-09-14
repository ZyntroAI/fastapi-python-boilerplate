// AI Context matcher — keyword / target / category scoring.
// Pure Node (CommonJS). No dependencies, no network, no credentials.
'use strict';

const RULES = require('./rules.json');

const TIER_WEIGHTS = RULES.tier_weights || {
  exact_target: 100,
  keyword: 40,
  category: 10,
};

const MAX_TEXT = 500;

function assertContext(context) {
  if (context === null || typeof context !== 'object' || Array.isArray(context)) {
    throw new TypeError('context must be a plain object');
  }
  if (typeof context.intent !== 'string' || context.intent.trim() === '') {
    throw new TypeError('context.intent is required and must be a non-empty string');
  }
  if (context.intent.length > MAX_TEXT) {
    throw new RangeError(`context.intent exceeds ${MAX_TEXT} characters`);
  }
  if (context.targets !== undefined) {
    if (!Array.isArray(context.targets)) {
      throw new TypeError('context.targets must be an array of skill ids');
    }
    const known = new Set(RULES.rules.map((r) => r.skill));
    for (const t of context.targets) {
      if (typeof t !== 'string' || !known.has(t)) {
        throw new TypeError(`unknown target skill: ${String(t)}`);
      }
    }
  }
  if (context.keywords !== undefined && !Array.isArray(context.keywords)) {
    throw new TypeError('context.keywords must be an array of strings');
  }
  if (context.mutates !== undefined && typeof context.mutates !== 'boolean') {
    throw new TypeError('context.mutates must be a boolean');
  }
  return true;
}

function normalise(value) {
  return String(value).toLowerCase().trim();
}

// Score one rule against the context. Returns { score, reasons }.
function scoreRule(rule, context) {
  const reasons = [];
  let score = 0;

  const targets = (context.targets || []).map(normalise);
  if (targets.includes(normalise(rule.skill))) {
    score += TIER_WEIGHTS.exact_target;
    reasons.push('exact_target');
  }

  const haystack = [
    normalise(context.intent || ''),
    ...(context.keywords || []).map(normalise),
  ].join(' ');

  const matched = [];
  for (const kw of rule.keywords || []) {
    const needle = normalise(kw);
    if (!needle) continue;
    // word-boundary match keeps "pr" from firing on "preview"
    const re = new RegExp(`(^|[^a-z0-9])${needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}([^a-z0-9]|$)`, 'i');
    if (re.test(haystack)) matched.push(needle);
  }
  if (matched.length > 0) {
    score += TIER_WEIGHTS.keyword * matched.length;
    reasons.push(`keyword:${matched.join(',')}`);
  }

  if (context.category && normalise(context.category) === normalise(rule.category)) {
    score += TIER_WEIGHTS.category;
    reasons.push('category');
  }

  return { score, reasons, matched_keywords: matched };
}

// Rank every skill for a context. Highest score first; ties broken by id.
function match(context) {
  assertContext(context);
  const ranked = RULES.rules
    .map((rule) => {
      const { score, reasons, matched_keywords } = scoreRule(rule, context);
      return {
        skill: rule.skill,
        category: rule.category,
        mutates: Boolean(rule.mutates),
        score,
        reasons,
        matched_keywords,
      };
    })
    .filter((r) => r.score > 0)
    .sort((a, b) => (b.score - a.score) || a.skill.localeCompare(b.skill));

  return { intent: context.intent, count: ranked.length, candidates: ranked };
}

// Convenience: the single best skill, or null.
function best(context) {
  const out = match(context);
  return out.candidates.length > 0 ? out.candidates[0] : null;
}

module.exports = { match, best, assertContext, TIER_WEIGHTS };
