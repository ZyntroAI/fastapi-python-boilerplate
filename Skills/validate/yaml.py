import yaml

def validate_yaml_syntax(path: str) -> dict:
    try:
        with open(path) as f:
            yaml.safe_load(f)
        return {"ok": True}
    except yaml.YAMLError as e:
        return {"ok": False, "error": str(e)}
