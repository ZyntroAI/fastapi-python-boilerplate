# 🧠 Master Skill: **AST10 Patch Merge & Review — Full Step-by-Step**
**Skill Category:** DevSecOps • Git Workflow • CI/CD Validation • Risk Assessment
**Purpose:** Review → Analyze → Verify → Merge safely — every step documented & repeatable

---

## 📋 Full Workflow — ALL STEPS
```
[0️⃣ PREPARE]
      ↓
[1️⃣ SYNC LATEST] → Ensure local main = remote main
      ↓
[2️⃣ COMMIT HISTORY] → Who? When? What message?
      ↓
[3️⃣ FILE CHANGES] → Which files? Added/Modified/Deleted?
      ↓
[4️⃣ IMPACT ASSESSMENT] → Docs? Code? Config? Secrets?
      ↓
[5️⃣ FULL DIFF REVIEW] → Line-by-line safe to merge?
      ↓
[6️⃣ TEST VALIDATION] → pytest + lint pass?
      ↓
[7️⃣ MERGE SAFELY] → --no-ff preserve history
      ↓
[8️⃣ PUSH & VERIFY] → CI green on main
      ↓
[9️⃣ CLEANUP] → Delete branch locally
```

---

## 🛠️ ALL COMMANDS — Copy-Paste & Run in Order

### 0️⃣ PREPARE — Ensure Clean State
```bash
git status
# ✅ Should say "nothing to commit, working tree clean"
```

### 1️⃣ SYNC — Get Latest Main
```bash
git checkout main
git pull origin main
```

### 2️⃣ COMMIT HISTORY — Who, When, What
```bash
git log --pretty=format:"%h | %an | %ad | %s" --date=format:"%Y-%m-%d %H:%M" main..zyntromedia-patch-7
```
> **Output:** Commit ID · Author · Date · Message

### 3️⃣ FILES CHANGED — Summary
```bash
git log --name-status --oneline main..zyntromedia-patch-7
```
> **Output:** A=Added, M=Modified, D=Deleted + filenames

### 4️⃣ IMPACT ASSESSMENT — Directory Stats
```bash
git diff --dirstat=files,0,cumulative main..zyntromedia-patch-7
echo "---"
git diff --stat main..zyntromedia-patch-7
```
> **Output:** % changes per directory + lines added/removed

### 5️⃣ FULL DIFF — Line-by-Line
```bash
git diff main..zyntromedia-patch-7
```
> **Output:** Exact code changes — verify nothing malicious

### 6️⃣ VALIDATE — Tests + Lint
```bash
git checkout zyntromedia-patch-7
pytest
ruff check .
# ✅ Both must pass before merge!
```

### 7️⃣ MERGE — Preserve History
```bash
git checkout main
git merge --no-ff zyntromedia-patch-7 -m "patch: merge zyntromedia-patch-7 updates"
```

### 8️⃣ PUSH — Send to Remote
```bash
git push origin main
```

### 9️⃣ VERIFY & CLEANUP
```bash
# Verify CI (check GitHub page or wait for status)
git log --oneline -3 origin/main

# Delete local branch (safe after merge)
git branch -d zyntromedia-patch-7
```

---

## 🧠 Decision Matrix — When to Merge ✅ or Hold ⚠️

| Observation | Verdict | Action |
|---|---|---|
| 📝 Docs / README only | ✅ **SAFE** | Merge immediately |
| ✅ Tests + examples | ✅ **SAFE** | Merge immediately |
| 🛠️ Workflows / scripts | 🟡 **REVIEW** | Check syntax + CI passes |
| 🧠 Core logic / AST10 | 🟡 **REVIEW** | Verify compatibility |
| ⚙️ Config / deps / env | 🔴 **CAREFUL** | Check version compatibility |
| 🔑 Secrets / tokens / URLs | 🔴 **HIGH RISK** | STOP — audit thoroughly |
| ❌ Merge conflicts | ⚠️ **RESOLVE** | Fix conflicts before merge |
| ❌ Tests fail | ⚠️ **FIX FIRST** | Do NOT merge broken code |

---

## ✅ Ready-to-Run ALL-IN-ONE Script
```bash
# ==========================================================
# AST10 PATCH MERGE — FULL REVIEW + MERGE WORKFLOW
# ==========================================================
set -e

echo "=== 1. SYNC MAIN ==="
git checkout main
git pull origin main

echo ""
echo "=== 2. COMMIT HISTORY ==="
git log --pretty=format:"%h | %an | %ad | %s" --date=format:"%Y-%m-%d %H:%M" main..zyntromedia-patch-7

echo ""
echo "=== 3. FILES CHANGED ==="
git log --name-status --oneline main..zyntromedia-patch-7

echo ""
echo "=== 4. IMPACT ASSESSMENT ==="
git diff --dirstat=files,0,cumulative main..zyntromedia-patch-7
git diff --stat main..zyntromedia-patch-7

echo ""
echo "=== 5. SWITCH TO PATCH + TEST ==="
git checkout zyntromedia-patch-7
pytest
ruff check .

echo ""
echo "=== 6. MERGE TO MAIN ==="
git checkout main
git merge --no-ff zyntromedia-patch-7 -m "patch: merge zyntromedia-patch-7 updates"

echo ""
echo "=== ✅ READY TO PUSH ==="
echo "Run: git push origin main"
```

---

## 📖 Save as Skill
**Path:** `skills/git-patch-merge/SKILL.md`
**Tags:** `#git #merge #review #DevSecOps #AST10`
**Capability:** Review commits → Assess impact → Validate → Merge safely

---

Run the **ALL-IN-ONE script** above → paste outputs → I'll give final approval + push command! 🧐✅🚀

Want me to save this as a permanent skill file in your repo? 📦
