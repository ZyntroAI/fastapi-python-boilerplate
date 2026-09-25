def create_blocker(permission: str, required: str, granted: bool):
    return {
        "type": "permission",
        "permission": permission,
        "required": required,
        "granted": granted,
        "resolution": f"Grant {permission}: {required} to this token"
    }
