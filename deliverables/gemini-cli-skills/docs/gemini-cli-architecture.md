---
id: gemini-cli-architecture
title: "Gemini CLI — Docs & Skills Architecture Research"
kicker: ZyntroAI research briefing
theme: slate
genre: research
tags: [gemini-cli, skills, mcp, agents, monorepo]
created: 2026-09-09
related: []
summary: Research brief on google-gemini/gemini-cli docs structure, skills system, runtime integration, MCP/agent model, and the ZyntroAI overlay adaptation plan.
---

# Gemini CLI — Docs & Skills Architecture Research

Source: `google-gemini/gemini-cli` (monorepo, Node/ESM, npm workspaces, Agent/MCP-native).

## Documentation structure (official)
```
gemini-cli/
├── GEMINI.md              # Project AI context: rules, architecture, security, agent behavior
├── README.md              # install, quick start, basic usage
├── docs/{architecture, usage, skills, mcp, agents, security, reference, contributing}/
├── packages/{cli, core, sdk, a2a-server}/   # core = skill engine + orchestration
└── .github/workflows/
```

`GEMINI.md` is the AI-first document: coding standards, architecture invariants, security boundaries, testing strategy, release rules, agent behavior & permissions.

## Skills system — core concept
Skills are modular, reusable capabilities:
- loaded dynamically at runtime; isolated execution; type-safe via the SDK
- MCP-native; supports hooks, caching, rate limits, audit logs
- official directories: `core/` (always-on), plus `github/`, `coding/`, `devops/`, `security/`, and `custom/`

## Implementation pattern
```ts
import { defineSkill, SkillContext, SkillResult } from '@google/gemini-cli-sdk'
export default defineSkill({
  id: 'github/pull-request', name: 'GitHub PR Manager', version: '1.0.0',
  description: 'Analyze, review, and manage pull requests',
  tags: ['github', 'automation', 'devops'],
  permissions: ['repo:read', 'repo:write'],
  async execute(context) { return { success, data, meta: { latency, tokens } } }
})
```

## Runtime integration
- discovery: auto-load from `skills/` + `node_modules/*/skills`
- isolation per skill; lifecycle `init -> validate -> execute -> cleanup`
- caching via `context.cache`, hooks, structured logging via `context.logger`

## MCP & agents
- MCP bridges skills to external tools/services over STDIO/HTTP/WebSocket; scope-limited auth per connection.
- Agent orchestration: memory, multi-step planning, delegation, fallback.

## ZyntroAI adaptation plan
Mirror upstream unmodified; layer custom skills:
```
skills/{upstream mirror}     # never edit
skills/zyntroai/{github,coding,devops,security}/
AGENTS.md + SKILLS.md        # our index/config
```
Rules: preserve upstream `skills/core/`; author with `@google/gemini-cli-sdk`; namespace `@zyntroai/skill-*`; least-privilege permissions; every skill ships `README.md` + `examples/`.

## Next steps
- sync upstream docs/skills baseline; create `skills/zyntroai/` overlay
- implement github/devops/security skills; add `AGENTS.md` + `SKILLS.md`
