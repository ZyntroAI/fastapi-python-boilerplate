from ..scan.structure import validate_structure
from ..repair.permissions import audit_permissions

def full_validate(data: dict) -> dict:
    structure = validate_structure(data)
    perms = audit_permissions(data)
    return {
        "pass": structure["ok"] and perms["ok"],
        "structure": structure,
        "permissions": perms
    }
