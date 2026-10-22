# GitHub Copilot CLI — Operational Standards

Source: GitHub's "Getting started with GitHub Copilot CLI" doc. Scope: how the CLI should be invoked, gated, and scripted in day-to-day and automated use.

## 1. Invocation Mode Selection

- **Interactive (`copilot`)** — default for exploratory work, multi-turn tasks, anything where you want to review and approve changes step by step.
- **Non-interactive (`copilot -p "prompt"`)** — for one-shot lookups, scripted tasks, and automation. Suited to CI hooks or shell scripts where a single answer is enough.
- **`-s` flag** — always pair with `-p` when the output will be parsed or piped into another tool (`copilot -sp "..."`). It strips usage/metadata and returns only the response.

## 2. Context Provisioning

- Use `@` to explicitly mention files rather than relying on Copilot to infer scope from the working directory.
- Keep prompts scoped to only the files relevant to the task — avoid mentioning entire directories when a handful of files will do.

## 3. Trust & Approval Gating

- On first use in a new project directory, the CLI asks you to confirm the directory's files are suitable for AI use. Treat this as a real checkpoint, not a rubber stamp — verify there's nothing sensitive or unreviewed in scope before confirming.
- Copilot will not modify files without explicit approval. Never pre-approve a batch of changes sight unseen; review each diff.
- For non-interactive/scripted use (`-p`), treat Copilot's output as a suggestion to be reviewed downstream, not as an auto-applied change — the approval gate that exists in interactive mode doesn't carry over to scripting.

## 4. Authentication

- `/login` is a one-time step per machine/environment (interactive session only).
- For CI or automated environments, use pre-authenticated credentials in the environment rather than triggering interactive `/login`.

## 5. Installation & Environment

- npm path requires **Node.js 22+**: `npm install -g @github/copilot`.
- Platform-native installers are equally supported: WinGet (Windows), Homebrew cask (`copilot-cli`, macOS/Linux).
- Standardize on one install method per team/environment to avoid version drift across machines.

## 6. Scripting Conventions

- Default script pattern: `copilot -sp "PROMPT"` — response-only output, safe to pipe or capture in a variable.
- Consult `copilot help TOPIC` for flag-specific behavior rather than assuming; flags beyond `-p`/`-s` should be verified before relying on them in automation.

## 7. Interactive Shortcuts (reference)

| Shortcut | Action |
| --- | --- |
| `Esc` | Cancel current operation |
| `Ctrl+C` | Cancel / clear input / exit |
| `Ctrl+L` | Clear screen |
| `@` | Mention files for context |
| `/` | Slash commands |
| `?` | Tabbed help |
| `↑` / `↓` | Command history |

Full reference: `/help` inside an interactive session.

## 8. Out of Scope

- No external write-safeguard is needed for interactive mode — the built-in approval gate covers it.
- Voice input is an optional convenience, not an operational dependency.

## 9. CI Mapping — Example: `ZyntroAI/fastapi-python-boilerplate`

No target repo was specified, so this uses your general-purpose FastAPI boilerplate as the reference — swap the repo/workflow name if a different one applies. The example wires §1 and §6's `-sp` convention into a PR-summary job.

```yaml
# .github/workflows/copilot-pr-summary.yml
name: copilot-pr-summary
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  summarize:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write   # comment only — no repo write access
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install GitHub Copilot CLI
        run: npm install -g @github/copilot

      - name: Generate PR summary (read-only)
        env:
          COPILOT_TOKEN: ${{ secrets.COPILOT_CLI_TOKEN }}
        run: |
          git diff "origin/${{ github.base_ref }}...HEAD" > diff.txt
          cat diff.txt | copilot -sp "Summarize this diff for a PR description. Flag any risky changes." > summary.txt

      - name: Post summary as PR comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.readFileSync('summary.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body,
            });
```

**How this maps back to the standards:**

| Standard | How the job honors it |
| --- | --- |
| §1 — Non-interactive mode | Uses `copilot -sp`, not interactive `copilot` |
| §2 — Context provisioning | Scoped to the PR diff only, not the whole checked-out repo |
| §3 — Approval gating | CI has no human approval prompt, so the job never auto-applies changes — it only posts a comment (a suggestion), and `permissions` is capped to `pull-requests: write` with no `contents: write` |
| §4 — Authentication | Token comes from a repo secret (`COPILOT_CLI_TOKEN`), not interactive `/login` |
| §6 — Scripting convention | `-sp` output is piped directly into the next step, no manual parsing of usage metadata |

**Guardrail specific to CI:** because §3's human-in-the-loop approval doesn't exist in an automated job, the workflow's `permissions` block is the substitute safeguard — never grant `contents: write` to a job that runs Copilot CLI non-interactively unless a separate human-reviewed step gates the actual commit.