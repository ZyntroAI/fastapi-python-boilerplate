import yaml

def validate_syntax(text: str) -> dict:
    try:
        yaml.safe_load(text)
        return {"pass": True}
    except yaml.YAMLError as e:
        return {"pass": False, "error": str(e)}
