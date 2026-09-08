from .workflow_files import is_workflow_file

def infer_required_permissions(changed_files: list[str]) -> dict:
    """Map changed files → required GitHub scopes"""
    needs_workflow = any(is_workflow_file(f) for f in changed_files)
    return {
        "contents": "write",
        "workflows": "write" if needs_workflow else None
    }
