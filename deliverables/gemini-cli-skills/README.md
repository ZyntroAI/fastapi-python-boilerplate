# Gemini CLI — Docs & Skills Architecture

Research deliverable for extending `google-gemini/gemini-cli` with a **ZyntroAI overlay layer** of custom skills. The gemini-cli repo is a monorepo (Node/ESM, npm workspaces) whose `packages/core` is the **Skill Engine**; skills are modular capabilities loaded dynamically at runtime, isolated, type-safe via `@google/gemini-cli-sdk`, and MCP-native.

## Contents
- `docs/gemini-cli-architecture.md` — full research brief (structure, skills system, runtime, MCP/agents, adaptation plan)
- `AGENTS.md` — ZyntroAI agent config (overlay rules)
- `SKILLS.md` — skills registry & index
- `templates/` — ready-to-use skill templates
  - `templates/skill-template.ts` — canonical `defineSkill` implementation
  - `templates/zyntroai/<category>/<skill>/` — example skills (github/pull-request, coding/typescript, devops/ci-cd, security/secret-scan)

## Key rules (overlay)
1. Never edit upstream `skills/core/` — always overlay.
2. Always author against `@google/gemini-cli-sdk`.
3. Namespace custom skills as `@zyntroai/skill-*`.
4. Declare explicit, least-privilege permissions.
5. Each skill ships a `README.md` + `examples/`.

> Place this directory as `deliverables/gemini-cli-skills/` in `fastapi-python-boilerplate`. To apply to a ZyntroAI fork of gemini-cli, mirror `templates/zyntroai/` as `skills/zyntroai/` and drop `AGENTS.md`/`SKILLS.md` at repo root (upstream `GEMINI.md` stays untouched).
