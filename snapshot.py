import json
from datetime import datetime
from pathlib import Path

def create_snapshot(branch, commit, blocker, files, validation):
    return {
        "branch": branch,
        "commit": commit,
        "blocker": blocker,
        "files": files,
        "validation": validation,
        "created_at": datetime.utcnow().isoformat()
    }

def save_snapshot(snapshot, path=".handoff.json"):
    Path(path).write_text(json.dumps(snapshot, indent=2))

def load_snapshot(path=".handoff.json"):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None
