from permission_aware_git.git_ops import current_branch, latest_commit, changed_files

def capture_state():
    return {
        "branch": current_branch(),
        "commit": latest_commit(),
        "files": changed_files(),
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }
