# Gemini CLI — Docs & Skills Architecture

Research deliverable for extending `google-gemini/gemini-cli` with a **ZyntroAI overlay layer**
of skills. `gemini-cli` is a monorepo (Node/ESM, npm workspaces) whose `packages/core` carries
the **skill engine**; skills are markdown-defined capabilities discovered at runtime and
activated through a core tool.

> **Corrected 2026-09-16.** This README previously described a TypeScript `defineSkill` API
> against `@google/gemini-cli-sdk`, with skills under `skills/core|github|coding|devops|security`.
> That was wrong. Skills are `SKILL.md` files with YAML frontmatter; the working set lives in
> `.gemini/skills/`. See `SKILLS.md` for the verified layout.

## Contents

- `SKILLS.md` — skills registry: how skills work, where they live, what exists today
- `AGENTS.md` — ZyntroAI agent config (overlay rules)
- `docs/gemini-cli-architecture.md` — research brief (structure, skills system, runtime, MCP/agents, adaptation plan)
- `templates/` — skill scaffolds
  - `templates/skill-template.ts` — legacy TypeScript template (kept for reference; **not** the real authoring format)
  - `templates/zyntroai/<category>/<skill>/` — example skill sketches

## How a skill is authored (verified)

A skill is a directory with a `SKILL.md`:

```markdown
---
name: code-reviewer
description:
  Use this skill to review code. Supports local changes and remote PRs.
---

# Code Reviewer
...instructions...
```

- `description` is the router — state plainly **when** to use the skill.
- Depth goes in sibling `references/` files; executables in `scripts/`.
- Discovery: `.gemini/skills/<name>/SKILL.md` in-repo, plus `packages/core/src/skills/builtin/`.
- Activation: the `activate-skill` tool in `packages/core/src/tools/`.

## Key rules (overlay)

1. Never edit upstream skill content — add new skill directories instead.
2. Author as `SKILL.md` + YAML frontmatter; do not invent a TypeScript authoring API.
3. Keep skills isolated; no global mutation.
4. Each skill should be readable standalone, with a `description` that routes correctly.
5. Keep `SKILLS.md` in step with reality — it is a registry, not an aspiration.

> Place this directory as `deliverables/gemini-cli-skills/` in `fastapi-python-boilerplate`.
> To apply to a ZyntroAI fork of gemini-cli, copy the skill directories into `.gemini/skills/`
> and drop `AGENTS.md`/`SKILLS.md` at repo root (upstream `GEMINI.md` stays untouched).
