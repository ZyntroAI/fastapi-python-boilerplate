# AI Agents UI — Design Tokens (Figma reference)

Semantic tokens for building/standardizing AI-assistant surfaces (chat, agent
status, execution, approval). Match the repo's dark-slate + semantic-color
convention — no literal colors in code.

## Color (semantic)
| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `color/bg/base` | `#FFFFFF` | `#0F172A` | app background |
| `color/bg/surface` | `#F8FAFC` | `#1E293B` | cards / panels |
| `color/border/default` | `#E2E8F0` | `#334155` | dividers, borders |
| `color/text/primary` | `#0F172A` | `#F1F5F9` | primary text |
| `color/text/muted` | `#64748B` | `#94A3B8` | secondary text |
| `color/accent/primary` | `#0F766E` | `#2DD4BF` | primary action, focus |
| `color/status/success` | `#15803D` | `#4ADE80` | agent done / pass |
| `color/status/warning` | `#B45309` | `#FBBF24` | needs approval |
| `color/status/error` | `#B91C1C` | `#F87171` | blocked / fail |
| `color/status/info` | `#1D4ED8` | `#60A5FA` | running / thinking |

## Typography
| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `type/display` | 32 / 1.25 | 700 | page / hero title |
| `type/title` | 20 / 1.4 | 600 | section title |
| `type/body` | 14 / 1.5 | 400 | default text |
| `type/caption` | 12 / 1.4 | 400 | helper, meta |
| `type/mono` | 13 | 400 | code / logs / tokens |

## Spacing / radius / shadow
- Spacing scale: 4 / 8 / 12 / 16 / 24 / 32 (multiples of 4).
- Radius: `radius/sm=6`, `radius/md=8`, `radius/lg=12`.
- Shadow (elevation for modals/approval): `shadow/modal` = 0 8px 24px rgba(2,6,23,0.18).

## Component states (agent status)
Thinking → Running → Awaiting approval → Done / Blocked, mapped to
`color/status/*` so UI can render state purely from tokens.
