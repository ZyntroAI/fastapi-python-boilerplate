
---

## 📁 docs/PULL_REQUESTS/EXAMPLE_COMPLETED.md
```markdown
## EXAMPLE — Completed PR

**Title:** `feature/add-markdown-code-extraction-skill`

**Type:** Feature
**Description:** Add `extract_code()` function to `skills/text_processor.py` — pulls fenced code blocks from markdown input.

**Changes:**
- New regex pattern in `text_processor.py`
- Updated `prompts/` templates to list tool
- README skills section refreshed
- All existing tests pass

**Compliance:**
- No network/file writes outside allowed paths ✅
- No eval/exec/subprocess introduced ✅
- Docs updated ✅

**Reviewer:** @Owner — Approved ✅
**Merged:** 2026-09-26
**Status:** Complete ✅
