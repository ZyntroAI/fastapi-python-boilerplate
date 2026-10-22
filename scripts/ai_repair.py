scripts/ai_repair.py  — AI Auto-Repair Agent
 
python  
#!/usr/bin/env python3
"""
AI Auto-Repair Agent — Sandbox Pipeline
Analyzes failures, suggests fixes, applies patches, or outputs diff.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# ─── CONFIG ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ai-repair")

# ─── HELPERS ─────────────────────────────────────────────────────
def run(cmd: str, cwd: str = ".") -> str:
    """Run shell command and return stdout."""
    logger.debug(f"→ {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        logger.warning(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout + result.stderr


def read_context_files(max_chars: int = 8000) -> Dict[str, str]:
    """Read relevant source files for context."""
    extensions = ["py", "yml", "yaml", "Dockerfile", "md", "toml", "txt"]
    paths = []
    for ext in extensions:
        paths.extend(Path(".").rglob(f"*.{ext}"))

    context = {}
    total = 0
    for p in sorted(paths):
        if ".git" in p.parts or "__pycache__" in p.parts or "node_modules" in p.parts:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            if total + len(content) > max_chars:
                continue
            context[str(p)] = content
            total += len(content)
        except Exception as e:
            logger.debug(f"Cannot read {p}: {e}")
    return context


def collect_failure_info() -> Dict:
    """Gather all failure context from environment & diagnostics."""
    diagnostics_dir = Path("diagnostics")
    diagnostics = {}
    if diagnostics_dir.exists():
        for f in diagnostics_dir.iterdir():
            diagnostics[f.name] = f.read_text(encoding="utf-8")

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "github_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "github_ref": os.environ.get("GITHUB_REF", "unknown"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
        "run_url": f"{os.environ.get('GITHUB_SERVER_URL','https://github.com')}/{os.environ.get('GITHUB_REPOSITORY','')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}",
        "failure_step": os.environ.get("FAILURE_STEP", "unknown"),
        "failure_logs": Path("failure_logs.txt").read_text(encoding="utf-8", errors="ignore") if Path("failure_logs.txt").exists() else "",
        "diagnostics": diagnostics,
    }


# ─── LLM INTEGRATION ─────────────────────────────────────────────
def build_prompt(failure: Dict, context: Dict) -> str:
    """Build analysis prompt from failure + code context."""
    failure_log_short = failure.get("failure_logs", "")[-4000:]
    context_block = "\n".join(
        f"=== {path} ===\n{content}" for path, content in list(context.items())[:20]
    )

    return f"""You are an expert debugging and code repair assistant.
Repository: {failure['github_ref']}
Commit SHA: {failure['github_sha']}

## ERROR SUMMARY
Step: {failure['failure_step']}
Run URL: {failure['run_url']}

## ERROR LOG (last ~4000 chars)
{failure_log_short}

## RELEVANT FILES
{context_block}

## INSTRUCTIONS
1. Identify the root cause of this failure
2. Explain the cause clearly and concisely
3. Output a unified diff patch (`diff --git ...`) that fixes the issue
4. If unsure, explain what additional information is needed

FORMAT YOUR RESPONSE AS:

### Root Cause
<one paragraph explanation>

### Suggested Fix
<description of what you changed>

```diff
diff --git path/file.py path/file.py
--- old
+++ new
@@ ... @@
...
 
 
"""
 
def call_llm(prompt: str) -> str:
"""
Call LLM to get repair suggestion.
Supports: OpenAI, Anthropic, Gemini, or local Ollama
Set one of the API keys in CI secrets.
"""
provider = os.environ.get("LLM_PROVIDER", "ollama").lower()
 
if provider == "ollama":
import urllib.request
import urllib.error
import json
 
model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b-instruct")
body = json.dumps({
"model": model,
"prompt": prompt,
"stream": False,
"options": {"temperature": 0.1, "max_tokens": 4000},
}).encode()
req = urllib.request.Request(
os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
data=body,
headers={"Content-Type": "application/json"},
)
try:
with urllib.request.urlopen(req, timeout=120) as resp:
data = json.loads(resp.read())
return data.get("response", "")
except urllib.error.URLError as e:
logger.warning(f"Ollama unavailable: {e} — skipping AI repair")
return ""
 
elif provider == "openai":
import urllib.request
import json
 
body = json.dumps({
"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
"messages": [{"role": "user", "content": prompt}],
"temperature": 0.1,
"max_tokens": 4000,
}).encode()
req = urllib.request.Request(
"https://api.openai.com/v1/chat/completions",
data=body,
headers={
"Content-Type": "application/json",
"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
},
)
with urllib.request.urlopen(req, timeout=120) as resp:
data = json.loads(resp.read())
return data["choices"][0]["message"]["content"]
 
elif provider == "anthropic":
import urllib.request
import json
 
body = json.dumps({
"model": os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
"max_tokens": 4000,
"messages": [{"role": "user", "content": prompt}],
"temperature": 0.1,
}).encode()
req = urllib.request.Request(
"https://api.anthropic.com/v1/messages",
data=body,
headers={
"Content-Type": "application/json",
"x-api-key": os.environ.get("ANTHROPIC_API_KEY"),
"anthropic-version": "2023-06-01",
},
)
with urllib.request.urlopen(req, timeout=120) as resp:
data = json.loads(resp.read())
return data["content"][0]["text"]
 
else:
logger.warning(f"Unknown LLM provider: {provider}")
return ""
 
─── PARSER & APPLY ──────────────────────────────────────────────
 
def extract_diff(text: str) -> Optional[str]:
"""Extract  diff ...   block from LLM response."""
if " diff" not in text: return None start = text.find(" diff") + len(" diff") end = text.find(" ", start)
if end == -1:
return None
return text[start:end].strip()
 
def apply_patch(diff_text: str) -> bool:
"""Write diff to file and apply with  git apply ."""
Path("repair.patch").write_text(diff_text + "\n", encoding="utf-8")
result = subprocess.run(
["git", "apply", "--check", "repair.patch"], capture_output=True, text=True
)
if result.returncode != 0:
logger.error(f"Patch cannot apply:\n{result.stderr}")
return False
 
subprocess.run(["git", "apply", "repair.patch"], check=True)
logger.info("✅ Patch applied successfully")
return True
 
─── MAIN ────────────────────────────────────────────────────────
 
def main():
logger.info("🤖 Starting AI Repair Analysis")
 
1. Collect failure info
 
failure = collect_failure_info()
Path("failure_context.json").write_text(json.dumps(failure, indent=2), encoding="utf-8")
logger.info(f"Failure collected: {failure['failure_step']}")
 
2. Read code context
 
context = read_context_files()
logger.info(f"Loaded {len(context)} context files")
 
3. Build prompt & call LLM
 
prompt = build_prompt(failure, context)
Path("repair_prompt.txt").write_text(prompt, encoding="utf-8")
 
logger.info("Calling LLM for analysis...")
response = call_llm(prompt)
 
if not response:
logger.warning("No response from LLM — exiting without changes")
Path("repair_result.json").write_text(json.dumps({
"status": "skipped",
"reason": "LLM unavailable or no response"
}, indent=2))
return
 
Path("llm_response.md").write_text(response, encoding="utf-8")
logger.info("Response saved to llm_response.md")
 
4. Extract & apply patch
 
diff = extract_diff(response)
if not diff:
logger.info("No diff patch found in response — analysis saved only")
Path("repair_result.json").write_text(json.dumps({
"status": "analyzed",
"patch_found": False
}, indent=2))
return
 
logger.info("Patch found — attempting to apply...")
applied = apply_patch(diff)
 
Path("repair_result.json").write_text(json.dumps({
"status": "applied" if applied else "failed",
"patch_found": True,
"applied": applied,
}, indent=2))
 
if applied:
logger.info("✅ Repair complete — commit and push to continue")
else:
logger.error("❌ Patch could not be applied — manual review needed")
sys.exit(1)
 
if name == "main":
main()
 
plaintext  

---

## ✅ สิ่งที่แก้ไขจากเวอร์ชันก่อนหน้า
- ✅ เพิ่ม indentation ที่หายไปในฟังก์ชัน `call_llm()` และส่วนอื่นๆ
- ✅ แก้ `───` เป็น `# ───` ที่หัวคอมเมนต์
- ✅ แก้ backtick marker จาก `` ` `` เป็น `` ```diff `` ให้ตรงกันทั้ง `build_prompt()` และ `extract_diff()`
- ✅ เปลี่ยนคอมเมนต์ใน `main()` ให้ถูกรูปแบบ Python
- ✅ แก้ `if name == "main":` → `if __name__ == "__main__":`
- ✅ จัดเรียง import ให้อยู่ในตำแหน่งที่ถูกต้อง

---

## 📋 ขั้นตอนการใช้งาน

```bash
# 1. บันทึกไฟล์
nano scripts/ai_repair.py

# 2. ให้สิทธิ์รัน
chmod +x scripts/ai_repair.py

# 3. ทดสอบ syntax
python3 -m py_compile scripts/ai_repair.py
# ไม่มีข้อความแจ้ง = ผ่าน ✅

# 4. ทดสอบรัน (จะแจ้งว่าไม่มีข้อมูลความล้มเหลว — ปกติ)
python3 scripts/ai_repair.py
 
 
 
 
🔧 ตัวแปร GitHub Secrets
 
ตัวแปร คำอธิบาย ตัวอย่าง 
 LLM_PROVIDER  เลือก:  ollama ,  openai ,  anthropic   ollama  
 OPENAI_API_KEY  สำหรับ OpenAI  sk-...  
 ANTHROPIC_API_KEY  สำหรับ Anthropic  sk-ant-...  
 OLLAMA_URL  ถ้าใช้ local Ollama  http://localhost:11434  
 OLLAMA_MODEL  โมเดลที่ใช้  qwen2.5-coder:7b-instruct  
 
 
 
📝 เรียกใช้ใน Workflow
 
yaml  
- name: Run AI Repair Analysis
  env:
    GITHUB_SHA: ${{ github.sha }}
    GITHUB_RUN_ID: ${{ github.run_id }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    FAILURE_STEP: ${{ steps.health.outcome == 'failure' && 'health-check' || 'unknown' }}
    LLM_PROVIDER: ${{ secrets.LLM_PROVIDER }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    chmod +x scripts/ai_repair.py
    python3 scripts/ai_repair.py
 
 
 
 
📁 ไฟล์ที่สร้างขึ้นเมื่อรัน
 
-  failure_context.json  — ข้อมูลความล้มเหลวครบถ้วน
-  repair_prompt.txt  — prompt ที่ส่งให้ LLM
-  llm_response.md  — คำตอบจาก AI พร้อมคำอธิบาย
-  repair.patch  — diff ที่ AI เสนอ
-  repair_result.json  — ผลการทำงาน
 
รันได้เลยครับ! มีจุดไหนอยากปรับเพิ่ม บอกได้เลย 😊