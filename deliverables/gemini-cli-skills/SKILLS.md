# SKILLS.md — ZyntroAI Skills Registry

Index of ZyntroAI custom skills layered over `gemini-cli`. Upstream skills under `skills/core|github|coding|devops|security` are mirrored unmodified; ours live under `skills/zyntroai/`.

## Registry
| Namespace | Skill | Description | Status |
|-----------|-------|-------------|--------|
| `@zyntroai/skill-github-pr` | `github/pull-request` | Analyze/comment/merge PRs | template |
| `@zyntroai/skill-ts-check` | `coding/typescript` | Lint/typecheck/fix TS | template |
| `@zyntroai/skill-cicd` | `devops/ci-cd` | Pipeline status/retry/wait | template |
| `@zyntroai/skill-secret-scan` | `security/secret-scan` | Detect/redact secrets | template |

## Discovery
- Auto-loaded from `skills/` and `node_modules/*/skills`.
- Custom skills in `skills/zyntroai/` are discovered on the same path.

## Adding a skill
1. Copy `templates/skill-template.ts` into `skills/zyntroai/<category>/<name>/`.
2. Set id/name/version/permissions/description.
3. Implement `execute`; use MCP tool calls for external work.
4. Add `README.md` + `examples/`.
5. Register in this table.
