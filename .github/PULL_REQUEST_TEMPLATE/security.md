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
