---
name: ⚙️ Configuration
about: Env, Docker, K8s, CI, infra-as-code
title: "config: "
---

## ⚙️ Infra/Config

### What is being changed
Describe the infra/config change (env, Docker, K8s, CI, IaC).

### Scope
- [ ] Environment / secrets config
- [ ] Docker / docker-compose
- [ ] Kubernetes manifests
- [ ] CI/CD workflows
- [ ] Observability / monitoring
- [ ] Other: _____

### Impact
- [ ] Existing behavior preserved (additive)
- [ ] Services affected: _____

### Validation
- [ ] YAML validated
- [ ] Config values correct (no secrets committed)
- [ ] Local parity confirmed (docker compose up)
- [ ] Rollback path defined

### Test evidence
```
(paste validation output)
```

### Checklist
- [ ] Change is minimal and targeted
- [ ] No secrets committed
- [ ] Documented in README / runbook where needed
- [ ] Rollback documented
