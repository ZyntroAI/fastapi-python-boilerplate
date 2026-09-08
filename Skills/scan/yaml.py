import yaml
from pathlib import Path

def load_yaml(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_yaml_raw(path: str):
    return Path(path).read_text(encoding="utf-8")
