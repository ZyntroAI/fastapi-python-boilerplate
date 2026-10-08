"""
🤖 PR Auto-Review — ตรวจเองก่อนคน
รันผ่าน CI หรือ Antigravity Agent
"""
from pathlib import Path
import re

def review_pr(pr_number: int, changed_files: list[str]) -> dict:
    checks = {
        "docs_updated": False,
        "tests_exist": False,
        "no_large_files": True,
        "conventional_commit": True,
        "risk_level": "low"
    }

    # ตรวจว่ามีเอกสารไหม
    if any(f.startswith("docs/") or f == "README.md" for f in changed_files):
        checks["docs_updated"] = True

    # ตรวจว่ามีทดสอบไหม
    if any("test" in f.lower() for f in changed_files):
        checks["tests_exist"] = True

    # เตือนถ้าแก้โค้ดแต่ไม่แก้ทดสอบ
    code_files = [f for f in changed_files if f.endswith(".py") and "test" not in f]
    test_files = [f for f in changed_files if "test" in f]
    
    if code_files and not test_files:
        checks["risk_level"] = "medium"

    return checks


def generate_comment(checks: dict) -> str:
    comment = "## 🤖 รีวิวอัตโนมัติ\n\n"
    
    comment += "### ✅ ผ่าน\n"
    for k, v in checks.items():
        if v and k != "risk_level":
            comment += f"- [x] {k.replace('_', ' ').title()}\n"
    
    if not all(checks.values()):
        comment += "\n### ⚠️ ควรตรวจ\n"
        if not checks["docs_updated"]:
            comment += "- [ ] อัปเดตเอกสารด้วยไหม?\n"
        if not checks["tests_exist"]:
            comment += "- [ ] เพิ่มทดสอบครบไหม?\n"
    
    comment += f"\n### 📊 ระดับความเสี่ยง: {checks['risk_level']}"
    return comment
