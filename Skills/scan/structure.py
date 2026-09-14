REQUIRED_TOP_LEVEL = ["name", "on", "jobs"]

def validate_structure(data: dict) -> dict:
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in data]
    return {
        "ok": len(missing) == 0,
        "missing": missing
    }
