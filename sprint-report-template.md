# [Project Name] — Sprint [N] Final Report

**Date:** YYYY-MM-DD
**Duration:** ~X hours
**Manager / Agent:** Claude
**Code Written By:** Human + Claude

---

## ⚡ TL;DR

<!-- 2-3 sentences max. State what works, what doesn't, and the #1 priority for next sprint. -->
[One-line status] — [what's now usable] — แต่ [known blocker/risk] ยังไม่ fix — priority sprint หน้าคือ [X]

---

## 🏆 What Was Accomplished

[1-2 sentence summary of the sprint in Thai, same as before]

### Stats

<!--
Generate these from git, don't hand-estimate:
  git log --since="<sprint-start>" --oneline | wc -l          # commits
  git diff --stat <start-commit>..HEAD | tail -1               # files changed, LOC
If any number below is NOT pulled from git, mark it "(estimated)" so it's not
mistaken for a verified figure when someone reviews this later.
-->

| Metric | Value | Source |
| --- | --- | --- |
| Lines of Code | [N] | `git diff --stat` |
| Files Changed | [N] | `git diff --stat` |
| Tasks Completed | [X/Y] | ClickUp list `901819462047` |
| Commits | [N] | `git log --oneline \| wc -l` |

### Top Achievements

1. [Achievement 1]
2. [Achievement 2]
3. [Achievement 3]
4. [Achievement 4]

---

## 🌏 Current State of Product

**Stack:** [tech stack]

- [Capability 1]
- [Capability 2]
- [Capability 3]

**Key Files:**

- `/path/to/file — one-line purpose`
- `/path/to/file — one-line purpose`

---

## 🐛 Issues & Bugs

<!--
Every row should be actionable, not just descriptive. Owner and ClickUp Task
start blank — fill in during sprint planning, not during report writing.
Link back to milestone list 901819462047 once a task ID exists.
-->

| ID | Severity | Issue | Owner | ClickUp Task |
| --- | --- | --- | --- | --- |
| BUG-001 | HIGH | [description] | — | — |
| BUG-002 | MEDIUM | [description] | — | — |
| BUG-003 | LOW | [description] | — | — |

---

## ⚠️ Known Limitations (not bugs, but flag before scope expands)

<!--
Things that "work as coded" but represent risk if usage grows — e.g. no
undo (data-loss risk), no concurrent-write handling, no auth on an endpoint.
These are easy to forget because nothing is "broken" yet.
-->

- **[Data safety]** [e.g. No undo/redo — a wrong placement cannot be reverted]
- **[Concurrency]** [e.g. SQLite + dev server — concurrent writes from 2+ users untested]
- **[Other]** [...]

---

## 📋 Recommended Next Sprint Tasks

<!--
Each task needs: what "done" looks like + a rough estimate, so sprint
planning can check capacity instead of guessing.
-->

### 🔴 HIGH PRIORITY

1. **[FE/BE] [Task name]** — [acceptance criteria: what counts as done]. *(Est: Xh)*
2. **[FE/BE] [Task name]** — [acceptance criteria]. *(Est: Xh)*

### 🟡 MEDIUM PRIORITY

1. **[FE/BE] [Task name]** — [acceptance criteria]. *(Est: Xh)*

### 🟢 LOW PRIORITY

1. **[FE/BE] [Task name]** — [acceptance criteria]. *(Est: Xh)*

---

## 🔧 Technical Notes

- Env/secrets: [e.g. GROQ_API_KEY in .env] — **confirmed in `.gitignore`?** [Y/N]
- Runtime requirements: [e.g. Python 3.11+]
- Install/run: `[command]`
- [Any other environment-specific gotcha]

---

*Report generated — [Project Name] Sprint [N] — YYYY-MM-DD*
