REQUIRED = ["name", "on", "jobs"]

def validate_schema(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"pass": False, "error": "not a dict"}
    missing = [k for k in REQUIRED if k not in data]
    return {"pass": not missing, "missing": missing}
