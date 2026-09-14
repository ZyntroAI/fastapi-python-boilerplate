# AGENTS.md — ZyntroAI Agent Configuration

Overlay rules for AI agents working on a ZyntroAI fork of `gemini-cli`. Complements upstream `GEMINI.md` (do not edit upstream).

## Branching & sync
- Treat `google-gemini/gemini-cli` as canonical upstream. Sync often; never commit directly into mirrored upstream paths.
- Our layer lives under `skills/zyntroai/` and root `AGENTS.md`/`SKILLS.md` only.

## Code & skills
- Author skills in TypeScript against `@google/gemini-cli-sdk` (`defineSkill`). Never hand-write the runtime contract.
- Namespace all custom skills `@zyntroai/skill-*`.
- Each skill: `id`, `name`, `version`, `description`, `tags`, `permissions[]`, `execute(context)` returning `{ success, data, meta }`.

## Security
- Permissions explicit and least-privilege (`repo:read`/`repo:write` only as needed).
- No secrets in code. Use MCP auth per connection; respect sandbox + path isolation.
- Guard PII/toxicity through `core/safety` skills rather than custom code.

## Testing & release
- Keep skills isolated (no global pollution); lifecycle `init -> validate -> execute -> cleanup`.
- Structured logging via `context.logger`; hooks `beforeExecute`/`afterExecute`/`onError`.
- Follow repo versioning rules; CHANGELOG entries for new skills.
