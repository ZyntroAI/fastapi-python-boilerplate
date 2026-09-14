import subprocess
import json
from pathlib import Path

def run_git(args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def current_branch():
    out, _, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return out

def latest_commit():
    out, _, _ = run_git(["rev-parse", "HEAD"])
    return out[:8]

def changed_files():
    out, _, _ = run_git(["diff", "--name-only", "HEAD"])
    return [f for f in out.split("\n") if f]

def push_with_retry(permission_check_fn):
    perm = permission_check_fn()
    if perm["result"] == "BLOCKED":
        return {
            "status": "BLOCKED",
            "error": perm.get("reason"),
            "retry_allowed": False
        }
    out, err, code = run_git(["push", "-u", "origin", current_branch()])
    return {"status": "OK" if code == 0 else "FAILED", "code": code, "stderr": err}
