# NotebookLM Access + Artifact Intelligence — Core P0

Runnable suite (resolver/access/artifact + validate/guide/security/provenance/verify/knowledge), pure stdlib.

## Usage
```python
from notebooklm_access import resolve, classify_access, route_artifact

res = resolve("https://notebooklm.google.com/notebook/<NB>/artifact/<ART>?utm=1")
# -> resource.notebook_id / artifact_id / canonical_url / tracking_removed

route_artifact(raw)      # artifact -> parent notebook (read-only)
classify_access(["login_redirect"])  # -> RESTRICTED (evidence-based)
```

## Test
```bash
python -m pytest notebooklm_access/tests/ -q    # 22 passed
```
