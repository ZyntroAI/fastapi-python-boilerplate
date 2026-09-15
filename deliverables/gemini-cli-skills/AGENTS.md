# AGENTS.md — ZyntroAI Agent Configuration

Overlay rules for AI agents working on a ZyntroAI fork of `gemini-cli`. Complements
upstream `GEMINI.md` (do not edit upstream).

> **Corrected 2026-09-16.** Earlier revisions described skills as TypeScript modules
> authored with `defineSkill` against `@google/gemini-cli-sdk`. That is not the real
> system. Skills are `SKILL.md` files with YAML frontmatter. See `SKILLS.md`.

## Branching & sync

- Treat `google-gemini/gemini-cli` as canonical upstream. Sync often; never commit
  directly into mirrored upstream paths.
- Sync is done by mirroring the upstream tree and preserving fork-owned files
  (do not let a tree mirror silently drop `.gitignore` hardening or fork tests).
- Our overlay adds new skill directories only — it does not modify upstream skills.

## Skills

- A skill is a directory containing `SKILL.md` with YAML frontmatter:
  `name` (kebab-case, matches the directory) and `description`.
- The `description` is the router. Write it to say **when** to activate the skill,
  not just what it does.
- Keep the body focused; move depth into sibling `references/` files and helpers
  into `scripts/`.
- Discovery is `.gemini/skills/<name>/SKILL.md` (repo) and
  `packages/core/src/skills/builtin/` (core). There is no root `skills/` tree.
- Activation runs through the `activate-skill` tool.

## Security

- No secrets in skill files. Use the surrounding auth/MCP layers, never inline tokens.
- Respect sandbox and path isolation; don't reach outside the skill's declared scope.
- Route PII/toxicity handling through core safety capabilities rather than custom code.

## Testing & release

- Keep skills isolated and independently readable.
- Verify a skill directory loads before claiming it works; a `SKILL.md` that the
  loader cannot parse is not a skill.
- Follow repo versioning rules; add a CHANGELOG entry for each new skill.
- Never describe the skill system in a way the repository does not support — registries
  drift into fiction faster than code does.

## Documentation integrity

`SKILLS.md` and this file are checked against the repository, not written from
memory. If a path or mechanism cannot be found in the tree, it does not belong here.
