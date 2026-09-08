import json
from pathlib import Path
from ..branch_cleanup.branch_state import capture_state

def generate_handoff(blocker: dict, validation: dict):
    state = capture_state()
    artifact = {
        "handoff": {
            "branch": state["branch"],
            "commit": state["commit"],
            "status": "BLOCKED",
            "blocker": blocker,
            "files": state["files"],
            "validation": validation,
            "next_action": "enable_workflows_permission"
        }
    }
    Path(".handoff.json").write_text(json.dumps(artifact, indent=2))
    return artifact
