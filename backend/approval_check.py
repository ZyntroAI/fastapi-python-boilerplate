import os
import json
from pathlib import Path

def has_approval_artifact(path: str = ".approval-granted.json") -> bool:
    if not Path(path).exists():
        return False
    data = json.loads(Path(path).read_text())
    return data.get("granted", False)
