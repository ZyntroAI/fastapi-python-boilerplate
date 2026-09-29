"""
ดึงทุกความคิดเห็นของ PR — ทั้งแบบทั่วไป • ตามบรรทัด • ตาม Commit
ใช้: python scripts/fetch_pr_comments.py 352
"""
import os
import sys
from github import Github

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "ZyntroAI/fastapi-python-boilerplate"

if not TOKEN:
    print("❌ ตั้งค่า GITHUB_TOKEN ก่อน")
    sys.exit(1)

g = Github(TOKEN)
repo = g.get_repo(REPO)
pr_num = int(sys.argv[1]) if len(sys.argv) > 1 else 352

print(f"{'='*60}")
print(f"📋 PR #{pr_num} — ทุกความคิดเห็น")
print(f"{'='*60}\n")

# 1. PR Comments (ทั่วไป)
print("💬 1. ความคิดเห็นทั่วไป:")
issue = repo.get_issue(pr_num)
for c in issue.get_comments():
    print(f"  • {c.user.login}: {c.body[:80]}...")

# 2. Line Comments (ตามบรรทัด)
print("\n✏️ 2. ความคิดเห็นตามบรรทัด:")
pr = repo.get_pull(pr_num)
for c in pr.get_comments():
    print(f"  • {c.path}:{c.position} — {c.user.login}: {c.body[:60]}...")

# 3. Commit Comments (ต่อแต่ละ Commit)
print("\n📌 3. ความคิดเห็นต่อ Commit:")
for commit in pr.get_commits():
    for c in commit.get_comments():
        print(f"  • {commit.sha[:7]} — {c.user.login}: {c.body[:60]}...")

print(f"\n✅ เสร็จสิ้น")
