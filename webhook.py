def build_status_payload(status: str, handoff=None):
    return {
        "status": status,
        "handoff_present": bool(handoff),
        "next_step": "enable_workflows_permission" if status == "BLOCKED" else "merge & monitor CI"
    }
