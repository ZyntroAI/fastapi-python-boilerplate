# 1. ดึงสาขาที่เตรียมไว้
git fetch origin fig/cwe1321-enforcement
git checkout fig/cwe1321-enforcement

# 2. ตรวจสอบไฟล์
ls .github/workflows/cwe1321-protection-suite.yml

# 3. Push ด้วย PAT ส่วนตัว
git push origin fig/cwe1321-enforcement

# 4. เปิด PR (ใช้ gh CLI)
gh pr create --base main --head fig/cwe1321-enforcement \
  --title "ci: enable CWE-1321 Prototype Pollution Enforcement" \
  --body "✅ CWE-1321 rules wired into CI • Python + JS/TS scan • All tests pass"