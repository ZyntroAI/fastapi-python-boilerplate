---
name: Default
about: General change (backend, frontend, knowledge, infra)
title: ""
labels: ""
assignees: ""
---

## Summary

<!-- What is changing and why? One clear paragraph. -->

## Type of change

- [ ] ✨ Feature (new capability)
- [ ] 🐛 Bugfix (fixes a defect)
- [ ] 🔒 Security (vulnerability / hardening)
- [ ] ⚙️ Configuration / Infra / CI
- [ ] 📚 Documentation
- [ ] 📦 Dependency
- [ ] 🚀 Release

> **Specialized template?** If your change is primarily **Security**, a
> **Release**, **Configuration/Infra**, **Documentation**, **Dependency** or a
> **Bugfix**, please use the matching typed template in
> [`.github/PULL_REQUEST_TEMPLATE/`](./PULL_REQUEST_TEMPLATE/) instead — each
> carries the checks the PR-quality CI expects for that type.

## Scope

- [ ] Backend (`backend/`)
- [ ] Frontend (`frontend/`)
- [ ] Knowledge / docs (`knowledge/`, docs)
- [ ] Infra / CI (`k8s/`, `.github/workflows/`)
- [ ] Other: _____

## What changed

<!-- Bullet list of the concrete changes. -->

## How tested

- [ ] Lint passes (ruff / eslint)
- [ ] Tests pass (pytest / vitest)
- [ ] Manual verification

```
(paste test / verification output)
```

## Checklist

- [ ] No secrets committed
- [ ] No unrelated changes bundled
- [ ] Existing files not clobbered (additive where appropriate)
- [ ] Changes are minimal and targeted
