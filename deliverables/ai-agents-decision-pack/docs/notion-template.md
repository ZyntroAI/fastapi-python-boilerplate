# AI Agents Comparison — Notion Template

Import this as a Notion database (table view). Columns are properties; rows are
agents you evaluate. Fill scores 1–5.

## Database properties
- **Agent** (title)
- **Category** (select): Code completion / Agentic editor / CLI agent / Platform
- **Capability** (number 1–5)
- **Efficiency** (number 1–5)
- **Security** (number 1–5)
- **Cost** (select): Free / Freemium / Paid
- **Stack fit** (select): Python / Node / Full-stack / General
- **Sandbox-gated exec** (checkbox)
- **Verdict** (select): Adopt / Trial / Watch / Reject
- **Notes** (text)

## Example rows (start here)
| Agent | Category | Capability | Efficiency | Security | Cost | Stack fit | Sandbox exec | Verdict |
|-------|----------|-----------|-----------|----------|------|-----------|--------------|---------|
| GitHub Copilot | Completion | 4 | 4 | 3 | Paid | General | ☐ | Trial |
| Claude Code | CLI agent | 5 | 4 | 3 | Paid | General | ☐ | Trial |
| Cursor | Editor | 4 | 3 | 3 | Freemium | Full-stack | ☐ | Watch |
| Fig | Platform | 3 | 4 | 5 | Tiered | Full-stack | ☑ | Adopt |

## Weighting (suggested)
Security 30% · Capability 25% · Efficiency 20% · Cost 15% · Stack fit 10%
