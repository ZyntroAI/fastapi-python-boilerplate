"""
📤 ซิงค์โน้ต Obsidian → GitHub
รันทุกวันผ่าน Scheduled Action
"""
from pathlib import Path
import subprocess
import os
from datetime import datetime

VAULT_PATH = Path(__file__).parent.parent / "docs" / "obsidian"
BRANCH = "main"

def run(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=VAULT_PATH).stdout

def sync():
    os.chdir(VAULT_PATH)
    
    # ดึงล่าสุดก่อน
    run("git pull origin main --rebase")
    
    # ตรวจการเปลี่ยน
    status = run("git status --porcelain")
    if not status.strip():
        print("✅ ไม่มีอะไรเปลี่ยน")
        return
    
    # บันทึกเวลา
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    run(f'git add . && git commit -m "🤖 sync: อัปเดตโน้ต {now}"')
    run("git push origin main")
    print(f"✅ ซิงค์เสร็จ — {status.count(chr(10))} ไฟล์")

if __name__ == "__main__":
    sync()
