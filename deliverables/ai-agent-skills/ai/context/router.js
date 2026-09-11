// AI Context router — turn matcher candidates into an executable plan.
// Applies the risk/approval policy, resolves progressive-disclosure layers,
// and refuses anything the skill's schema does not permit.
'use strict';

const { match } = require('./matcher');
const REGISTRY = require('../../registry.json');

const SKILL_BY_ID = new Map(REGISTRY.skills.map((s) => [s.id, s]));

// Actions that always need a human gate before they run.
const APPROVAL_SCOPES = [':write', ':send', ':invoke', ':purge', ':authorize'];

function needsApproval(scopes) {
  return (scopes || []).some((s) => APPROVAL_SCOPES.some((suffix) => s.endsWith(suffix)));
}

// Progressive disclosure: core is always on; the other two layers are decided
// by how much context we actually have.
function resolveLayers(context) {
  const layers = ['core'];
  if (context && (context.targets || context.mutates !== undefined)) {
    layers.push('essential');
  }
  if (context && context.constraints) {
    layers.push('situational');
  }
  return layers;
}

function route(context, options) {
  const opts = options || {};
  const limit = Number.isInteger(opts.limit) && opts.limit > 0 ? opts.limit : 3;
  const matched = match(context);

  const plan = [];
  for (const candidate of matched.candidates.slice(0, limit)) {
    const skill = SKILL_BY_ID.get(candidate.skill);
    if (!skill) continue;

    const scopes = skill.scopes || [];
    const approved = opts.approved_scopes || [];
    const missing = scopes.filter((s) => !approved.includes(s));

    const step = {
      skill: skill.id,
      name: skill.name,
      category: skill.category,
      path: skill.path,
      schema: skill.schema,
      layers: resolveLayers(context),
      score: candidate.score,
      reasons: candidate.reasons,
      mutates: candidate.mutates,
      required_scopes: scopes,
      missing_scopes: missing,
      approval_required: needsApproval(scopes),
      runnable: missing.length === 0 && !(needsApproval(scopes) && opts.dry_run !== false),
    };
    plan.push(step);
  }

  const blocked = plan.filter((s) => !s.runnable).length;
  return {
    intent: matched.intent,
    considered: matched.count,
    planned: plan.length,
    blocked,
    plan,
  };
}

module.exports = { route, resolveLayers, needsApproval };
