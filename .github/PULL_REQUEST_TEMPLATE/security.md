---
name: 🔒 Security
about: Vulnerability, auth, secrets, or security hardening
title: "security: "
---

## 🔒 Security

### Vulnerability / Issue
What is the security issue being addressed? (CVE, weakness, or risk)

### Affected area
- [ ] Authentication / Authorization
- [ ] Secrets / credentials handling
- [ ] Input validation / injection
- [ ] Data protection (encryption at rest / in transit)
- [ ] Dependency / supply-chain
- [ ] Other: _____

### Root cause
Describe the root cause and how it was identified.

### Fix
- [ ] Code change applied
- [ ] No secrets committed (scanned)
- [ ] Existing tests updated / new tests added
- [ ] Verified exploit no longer succeeds

### Impact
What is the blast radius if this is not fixed?

### Test evidence
```
(paste test output / proof the fix works)
```

### Checklist
- [ ] Security issue verified
- [ ] Change is minimal and targeted
- [ ] No plaintext secrets introduced
- [ ] Reviewer security-checks the diff

---

## 📄 `SECURITY.md` — เพิ่มนโยบาย SHA-Pinning
```markdown
# 🛡️ นโยบายความปลอดภัย — CI/CD
**อัปเดต:** 12 กันยายน 2026

## ✅ การปัก SHA (Supply Chain)
- **บังคับ:** ทุก GitHub Actions ต้องใช้ **full commit SHA** (40 ตัว)
- ❌ ห้าม: `@v4`, `@main`, `@latest`
- ✅ ตัวอย่างที่ถูกต้อง:
  ```yaml
  uses: actions/checkout@11bd71903a754fa4acce1b6cd295a12fc38ffd4
  uses: actions/setup-python@8d9ed9ac65efc6b600b45b871c877404878e487
