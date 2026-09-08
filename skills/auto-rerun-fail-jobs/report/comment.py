def build_comment(run_id: str, job_name: str, failure_type: str,
                  attempt: int, max_attempts: int, status: str, next_at: str = None) -> str:
    emoji = {
        "RETRYING": "🔄",
        "PASSED": "✅",
        "FAILED": "❌",
        "BLOCKED": "🚫",
        "DEBUG_HANDOFF": "🔧"
    }.get(status, "ℹ️")

    next_line = f"\n🔹 Next retry: {next_at}" if next_at else ""
    action = "Auto-retrying" if status == "RETRYING" else \
             "Handed to debug-error" if status == "DEBUG_HANDOFF" else \
             "Blocked — non-retryable" if status == "BLOCKED" else status

    return f"""<!-- auto-rerun-fail-jobs -->
{emoji} **CI Recovery Update**

🔹 Job: `{job_name}`
🔹 Failure: `{failure_type}`
🔹 Attempt: {attempt}/{max_attempts}
🔹 Status: {action}{next_line}

---
*Auto-Rerun Skill • {status}*
"""
