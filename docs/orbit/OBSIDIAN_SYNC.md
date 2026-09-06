# 🔄 Orbit ↔ Obsidian Sync
## 📌 Logic
- **Trigger**: Every main branch pipeline / scheduled daily
- **Path**: `/projects/crystalcastle/{file}.md`
- **Metadata**: Auto‑injected → `trace_id`, `version`, `env`

## 📄 Example Frontmatter
---
module: FullStack
status: active
trace_id: tr_abc123
updated: 2026-09-04
tags: [docs, synced, orbit]
---
