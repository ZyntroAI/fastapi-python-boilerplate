---
id: notebooklm-access-artifact-suite-v1
name: NotebookLM Access + Artifact Intelligence Suite
version: 1.1.0
visibility: public
dependencies: []
provides: [resolve, route_artifact, classify_access, validate_share, next_action, check_link, verify_access, build_knowledge_artifact]
auth_model: read-only, no auto-permission change, no auth bypass
---

# NotebookLM Access + Artifact Intelligence

Parse/normalize NotebookLM links, detect artifacts, classify access, validate
sharing, guide remediation, verify, and build knowledge — all read-only and
evidence-based.

## Modules
- resolver — parse/normalize, canonical URL, ids.
- artifact — route /artifact/<id> to parent.
- access — classify PUBLIC/RESTRICTED/PRIVATE/INVALID/UNKNOWN.
- validate — share_state (PUBLIC_OK / NOT_PUBLIC / URL_INVALID).
- guide — read-only remediation steps.
- link_security — HTTPS-only, strip tracking, reject creds.
- provenance — append-only access log.
- verify — bounded re-probe (wait -> probe -> confirm).
- knowledge — knowledge artifact when PUBLIC.

## Safety
Never bypass auth. Never change permissions automatically.
