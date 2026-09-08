from pathlib import Path

WORKFLOW_PATHS = [".github/workflows/"]

def is_workflow_file(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in WORKFLOW_PATHS) and path.endswith((".yml", ".yaml"))

def scan_workflow_files(root: str = "."):
    """Scan repo for workflow files"""
    root_path = Path(root)
    workflows = []
    for prefix in WORKFLOW_PATHS:
        path = root_path / prefix
        if path.exists():
            workflows.extend(str(f) for f in path.rglob("*.yml"))
            workflows.extend(str(f) for f in path.rglob("*.yaml"))
    return workflows
