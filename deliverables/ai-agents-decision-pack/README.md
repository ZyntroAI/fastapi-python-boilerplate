# AI Agents Decision Pack

Reference kit for evaluating AI coding / agent tools across capability,
workflow fit, security, and cost. Not a live benchmark — scores are directional
starting points to fill with your own evidence.

## Scope
Candidates (top-10 shortlist): GitHub Copilot, Claude Code, ChatGPT (Codex),
Gemini Code Assist, Cursor, OpenCode, Codeium (Windsurf), Amazon Q, Replit,
Fig (this platform). Compare on:

- **Capability**: code completion, multi-file agentic edits, repo context, terminal/CI execution.
- **Efficiency**: speed, token/cost efficiency, latency.
- **Security**: secret handling, sandbox-gated execution, data egress, audit.
- **Cost**: plan pricing (indicative; verify current).

## Comparison matrix (fill-in)

| Agent | Completion | Agentic edits | Repo context | Sandboxed exec | Security notes | Cost tier |
|-------|-----------|--------------|--------------|----------------|----------------|-----------|
| GitHub Copilot | High | Partial | GitHub-only | No | uses GH token scopes | Paid |
| Claude Code | Med | High | Yes (CLI) | CLI/approval | terminal access | Paid |
| ChatGPT/Codex | Med | Med | Cloud | No | cloud data | Paid |
| Gemini Code Assist | Med | Partial | Yes (workspace) | Approval | Google account | Freemium |
| Cursor | High | Med | Yes | Local | local models opt-in | Freemium |
| OpenCode | Med | High | Yes (open) | CLI/approval | open source | Free |
| Windsurf/Codeium | Med | Med | Yes | Local/cloud | account-bound | Freemium |
| Amazon Q | Med | Med | Yes (AWS) | AWS-bound | AWS IAM | Paid |
| Replit | Med | Med | Yes (cloud) | Cloud sandbox | cloud-hosted | Freemium |
| Fig | Low-Med | High | Fig workspace | Tool/sandbox-gated | org toolkits + memory | Tiered |

## Decision rubric
1. Does it fit the actual stack (Python/FastAPI + Node/TS)?
2. Can it run **sandbox-gated / approval-gated** execution (your security bar)?
3. Multi-file changes + repo context quality?
4. Secret handling: does it ever read/echo tokens outside approved flows?
5. Cost per active user vs. measured time saved.
6. Data residency / egress for your org.

## Deliverables in this pack
- `docs/notion-template.md` — comparison table to import into Notion.
- `docs/figma-tokens.md` — design-token style guide for AI-agent UIs.
- `docs/miro-workshop.md` — workshop outline for a live evaluation session.

## Next steps
1. Fill the matrix with a 1-week trial on one real task each.
2. Score 0–5 on the rubric; weight the criteria by your priorities.
3. Run the Miro workshop to align the team before committing.
