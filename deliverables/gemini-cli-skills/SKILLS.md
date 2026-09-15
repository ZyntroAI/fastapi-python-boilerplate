# SKILLS.md — ZyntroAI Skills Registry

Index of the gemini-cli skill system as it actually exists in `ZyntroAI/gemini-cli`
(fork of `google-gemini/gemini-cli`), plus the ZyntroAI overlay plan.

> **Corrected 2026-09-16.** The previous revision of this file described a
> TypeScript `defineSkill` / `@google/gemini-cli-sdk` system with skills under
> `skills/core|github|coding|devops|security`. That does not match the code.
> The real system is markdown-first — see below.

## How skills actually work

A skill is a **directory containing a `SKILL.md`** whose YAML frontmatter carries
`name` and `description`; the description is what the agent reads to decide when
to activate the skill. Everything else in the file is instructions.

```markdown
---
name: code-reviewer
description:
  Use this skill to review code. It supports both local changes and remote
  Pull Requests (by ID or URL).
---

# Code Reviewer
...instructions...
```

Supporting files (references, scripts, templates) live beside `SKILL.md` in the
same directory and are loaded on demand.

## Where skills live

| Location | Purpose |
|----------|---------|
| `.gemini/skills/<name>/SKILL.md` | Repository skills — the real, working set |
| `packages/core/src/skills/builtin/` | Skills compiled into core (`skill-creator`, `antigravity-support`) |
| `packages/core/src/skills/skillLoader.ts` | Discovery + load |
| `packages/core/src/skills/skillManager.ts` | Lifecycle + activation |
| `packages/core/src/tools/activate-skill.ts` | The agent-facing activation tool |
| `packages/sdk/src/skills.ts` | SDK surface for skill consumers |

**There is no root `skills/` directory, and no `skills/core|github|coding|devops|security` tree.**
Earlier revisions of this registry asserted those paths; they do not exist in the fork.

## Registry — skills present today (`.gemini/skills/`)

| Skill | Purpose |
|-------|---------|
| `agent-tui` | Terminal UI agent flows |
| `async-pr-review` | Lightweight PR review |
| `behavioral-evals` | Behavioural evaluation runs |
| `ci` | GitHub Actions monitoring, fail-fast triage, local CI replication |
| `code-reviewer` | Code review for local changes and remote PRs |
| `docs-changelog` | Changelog drafting from release templates |
| `docs-writer` | Writing/reviewing `docs/` and markdown |
| `github-issue-creator` | Issue creation |
| `pr-address-comments` | Resolving review comments on a PR |
| `pr-creator` | Opening pull requests |
| `review-duplication` | Duplicate-code review |
| `string-reviewer` | String/copy review against a word list |
| `tui-tester` | TUI testing |

Built in to core: `skill-creator`, `antigravity-support`.

## Adding a skill

1. Create `.gemini/skills/<name>/SKILL.md` (kebab-case directory name).
2. Write YAML frontmatter with `name` and `description` — the description is the
   router, so state plainly **when** to use it.
3. Put the instructions in the body. Keep it short; put depth in sibling
   `references/` files and executable helpers in `scripts/`.
4. Add the skill to the table above.

## Overlay plan (ZyntroAI)

ZyntroAI-specific skills are intended to live under **`.gemini/skills/`** alongside
the upstream ones, not in a separate root `skills/` tree. That directory does not
exist yet; it is created when the first overlay skill lands.

1. Never edit upstream skill content in place — add new skill directories instead.
2. Follow the frontmatter contract above (`name` + `description`); do not invent a
   TypeScript authoring API.
3. Keep claims about the runtime accurate: skills are markdown, discovered by the
   loader under `.gemini/skills/`, activated through the `activate-skill` tool.

## Sync status

`ZyntroAI/gemini-cli` `main` is at **`0.55.0-nightly.20260729.g3499c84f7`**.
Upstream `google-gemini/gemini-cli` `main` is at **`0.61.0-nightly`** — the fork is
behind. The sync branch exists only in the working environment; it has **not** been
pushed, and no PR is open, because writing to that repo is blocked at the
credential layer (`write_grant_required`).
