def ensure_permissions_block(data: dict) -> dict:
    """Ensure standard permissions block exists"""
    if "permissions" not in data:
        data["permissions"] = {
            "contents": "read",
            "id-token": "write"
        }
    return data
