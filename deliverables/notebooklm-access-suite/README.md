# NotebookLM Access + Artifact Intelligence — Core P0

Runnable core (link-resolver + access-check + artifact-router), pure stdlib.

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
python -m pytest notebooklm_access/tests/ -q    # 12 passed
```
