DANGEROUS_PERMS = ["write-all", "read-write-all"]

def audit_permissions(data: dict) -> dict:
    perms = data.get("permissions", {})
    issues = []
    for k, v in perms.items():
        if v in DANGEROUS_PERMS:
            issues.append(f"Dangerous permission: {k}: {v}")
    return {"ok": len(issues) == 0, "issues": issues}
