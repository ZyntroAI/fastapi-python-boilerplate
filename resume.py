from .snapshot import load_snapshot

def can_resume(path=".handoff.json") -> bool:
    snap = load_snapshot(path)
    if not snap:
        return False
    # Re-check permission now
    from workflow_permission_check.check.installation import validate_permissions
    ok = validate_permissions(snap["files"])["result"] == "PASS"
    if ok:
        import os; os.remove(path)
    return ok
