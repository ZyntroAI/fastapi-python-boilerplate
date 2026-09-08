---
id: credential-management
name: Central Credential Management
version: 2.0.0
type: core/security
metadata_only: true
zero_exposure: true
least_privilege: true
short_lived_lease: true
api: [resolve, lease, release, rotate, health, audit]
---

# Central Credential Management

Resolves short-lived credential leases via an external broker backed by a
vault / secret manager. This repo stores **metadata and references only** —
never raw secrets.

## Layers
- `app/core/credential_broker.py` — thin async broker client (no secret exposure)
- `app/skills/credential_management/client.py` — skill wrapper
- `credentials/registry.yaml` — metadata-only registry
