from .token import get_granted_scopes
from ..detect.required_permissions import infer_required_permissions

def validate_permissions(changed_files: list[str]):
    required = infer_required_permissions(changed_files)
    granted = get_granted_scopes()

    result = {}
    blocked = False
    for perm, req_level in required.items():
        if not req_level:
            continue
        has_scope = granted.get(perm, False)
        result[perm] = {
            "required": req_level,
            "granted": has_scope
        }
        if not has_scope:
            blocked = True

    return {
        "permission_check": result,
        "result": "BLOCKED" if blocked else "PASS",
        "reason": "missing_workflows_permission" if blocked else "ok"
    }
