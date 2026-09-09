---
name: 📦 Dependency
about: Package bump, upgrade, CVE remediation
title: "build(deps): "
---

## 📦 Dependencies

### Change
Which dependency and version change? (e.g. `package@1.2.3` → `@2.0.0`)

### Reason
- [ ] Routine update
- [ ] Security / CVE remediation (reference CVE)
- [ ] Feature needed upstream

### Compatibility
- [ ] Semver-compatible (patch/minor)
- [ ] Major version — breaking changes reviewed
- [ ] Transitive deps reviewed

### Validation
- [ ] Dependency review passed (CI)
- [ ] Tests pass with new version
- [ ] No known CVEs remain in the bump
- [ ] Lockfile / manifest updated together

### Test evidence
```
(paste test / audit output)
```

### Checklist
- [ ] Version pinned appropriately (not floating)
- [ ] Both manifest + lockfile updated
- [ ] CI green
- [ ] Change is isolated to the dependency
