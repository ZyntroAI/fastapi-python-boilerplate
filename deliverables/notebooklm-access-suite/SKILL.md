---
id: notebooklm-access-artifact-suite-v1
name: NotebookLM Access + Artifact Intelligence (Core P0)
version: 1.0.0
visibility: public
dependencies: []
provides: [resolve, classify_access, route_artifact]
auth_model: read-only, no auto-permission change, no auth bypass
---

# NotebookLM Access + Artifact Intelligence

Parse/normalize NotebookLM links, detect artifacts, classify access from
evidence — read-only, evidence-based only.

## Core P0 modules
- `resolver` — parse, normalize (strip /artifact + utm), canonical URL, ids.
- `access` — classify PUBLIC/RESTRICTED/PRIVATE/INVALID from evidence.
- `artifact` — route /artifact/<id> to parent notebook metadata.

## Safety
Never bypass auth. Never change permissions automatically. Classify from
evidence only.
