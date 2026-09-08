import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from workflow_permission-check.check.installation import validate_permissions
from workflow_repair.validate.workflow import full_validate
from workflow_repair.scan.yaml import load_yaml
from permission_aware_git.git_ops import changed_files, push_with_retry, current_branch, latest_commit
from branch_cleanup.handoff_generator import generate_handoff
from permission_escalation-request.request_builder import build_request, save_request
from handoff.snapshot import save_snapshot
from project_status_auto-update.board_sync import update_status

def main():
    print("🔍 Step 1: Permission Check")
    files = changed_files()
    perm = validate_permissions(files)

    if perm["result"] == "BLOCKED":
        print("❌ BLOCKED — Missing workflows: write")
        blocker = {
            "type": "permission",
            "permission": "workflows:write",
            "reason": perm.get("reason")
        }
        handoff = generate_handoff(blocker, validation={"status": "pending"})
        req = build_request(
            "github", "workflows:write",
            "Required to update .github/workflows/* (SHA pin compliance)",
            "ZyntroAI/new-crystalcastle", "zyntromedia"
        )
        save_request(req)
        update_status("BLOCKED", blocker)
        print("📋 Handoff + Permission Request Created")
        print("→ Grant permission → re-run this script to resume")
        return 1

    print("✅ Permissions OK")
    update_status("VALIDATING")

    # Validate workflow files
    wf_files = [f for f in files if f.startswith(".github/workflows/")]
    for wf in wf_files:
        data = load_yaml(wf)
        result = full_validate(data)
        if not result["pass"]:
            print(f"⚠️ {wf}: issues found")

    update_status("READY_TO_PUSH")
    print("🚀 Pushing...")
    result = push_with_retry(lambda: perm)
    print(result)
    update_status("PUSHED" if result["status"] == "OK" else "FAILED")
    return 0

if __name__ == "__main__":
    exit(main())
