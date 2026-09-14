from pathlib import Path
import yaml
from rules.yaml_rule import validate_syntax
from rules.schema_rule import validate_schema
from rules.sha_rule import validate_sha_pins

def validate_all(path: str):
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except:
        data = None

    return {
        "yaml": validate_syntax(text),
        "schema": validate_schema(data) if data else {"pass": False},
        "sha_pins": validate_sha_pins(text),
        "overall": all([
            validate_syntax(text)["pass"],
            validate_schema(data)["pass"] if data else False,
            validate_sha_pins(text)["pass"]
        ])
    }
