def collect_evidence(validation: dict) -> dict:
    return {
        "yaml_valid": validation.get("yaml", {}).get("pass", False),
        "schema_valid": validation.get("schema", {}).get("pass", False),
        "sha_pins_valid": validation.get("sha_pins", {}).get("pass", False),
        "ready_to_push": validation.get("overall", False)
    }
