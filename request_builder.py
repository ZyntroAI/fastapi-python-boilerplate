import json

def build_request(resource: str, permission: str, reason: str, repo: str, requester: str):
    return {
        "permission_request": {
            "resource": resource,
            "permission": permission,
            "reason": reason,
            "scope": {"repository": repo},
            "requested_by": requester,
            "risk": "high",
            "actions": ["push workflow fixes"],
            "approval_required": True
        }
    }

def save_request(artifact: dict, path: str = ".permission-request.json"):
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2)
