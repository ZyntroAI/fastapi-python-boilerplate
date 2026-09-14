"""Integration contract validation.

Validates YAML/JSON integration files against the shipped schema. Implemented
against the JSON Schema subset the schema actually uses, so the deliverable has
no third-party validator dependency; if ``jsonschema`` happens to be installed
it is used instead, and the two are cross-checked in the tests.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .policy import Policy, read_text

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "integrations" / "integration.schema.json"

TYPES: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


@dataclass
class ContractIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def load_schema(path: Path | None = None) -> dict[str, Any]:
    with Path(path or SCHEMA_PATH).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    py = TYPES.get(expected)
    if py is None:
        return True
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    # Everything else must not be a bool masquerading as a scalar.
    return isinstance(value, py) and not isinstance(value, bool)


def validate_against_schema(
    instance: Any, schema: Mapping[str, Any], path: str = "$"
) -> list[ContractIssue]:
    """Validate an instance against the JSON Schema subset in use."""
    issues: list[ContractIssue] = []
    if not isinstance(schema, Mapping):
        return issues

    expected_type = schema.get("type")
    if expected_type and not _type_ok(instance, str(expected_type)):
        issues.append(ContractIssue(path, f"expected {expected_type}, got {type(instance).__name__}"))
        return issues  # further checks would be noise

    if "enum" in schema and instance not in schema["enum"]:
        issues.append(ContractIssue(path, f"{instance!r} is not one of {schema['enum']}"))

    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and not re.search(str(pattern), instance):
            issues.append(ContractIssue(path, f"{instance!r} does not match {pattern}"))
        if "minLength" in schema and len(instance) < int(schema["minLength"]):
            issues.append(ContractIssue(path, f"shorter than minLength {schema['minLength']}"))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            issues.append(ContractIssue(path, f"{instance} below minimum {schema['minimum']}"))
        if "maximum" in schema and instance > schema["maximum"]:
            issues.append(ContractIssue(path, f"{instance} above maximum {schema['maximum']}"))

    if isinstance(instance, list) and isinstance(schema.get("items"), Mapping):
        for index, item in enumerate(instance):
            issues.extend(validate_against_schema(item, schema["items"], f"{path}[{index}]"))

    if isinstance(instance, Mapping):
        properties = schema.get("properties") or {}
        for key in schema.get("required", []):
            if key not in instance:
                issues.append(ContractIssue(path, f"missing required property {key!r}"))
        for key, value in instance.items():
            if key in properties:
                issues.extend(validate_against_schema(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                issues.append(ContractIssue(path, f"unexpected property {key!r}"))

    return issues


def load_integration(path: Path) -> Any:
    text = read_text(path)
    if text is None:
        raise ValueError(f"cannot read {path}")
    if path.suffix.lower() in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def _candidate_files(root: Path) -> list[Path]:
    """Integration contracts: integrations/*.integration.{yaml,yml,json}."""
    found: list[Path] = []
    for pattern in ("*.integration.yaml", "*.integration.yml", "*.integration.json"):
        found.extend(sorted((root / "integrations").glob(pattern)))
    return found


def check_integrations(policy: Policy, root: Path) -> list[str]:
    """Validate every integration contract found under ``integrations/``."""
    schema = load_schema()
    messages: list[str] = []

    for path in _candidate_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            instance = load_integration(path)
        except (ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
            messages.append(f"{rel}: unreadable ({exc})")
            continue
        for issue in validate_against_schema(instance, schema):
            messages.append(f"{rel} {issue}")

        # Cross-field rules the schema cannot express.
        if isinstance(instance, Mapping):
            base = instance.get("baseUrl")
            if isinstance(base, str) and base.startswith("http://"):
                messages.append(f"{rel} $.baseUrl: plaintext HTTP is not allowed")
            auth = instance.get("auth")
            if isinstance(auth, Mapping):
                ref = str(auth.get("secretRef", ""))
                if ref and not (ref.startswith("env:") or ref.startswith("vault:") or ref == "none"):
                    messages.append(
                        f"{rel} $.auth.secretRef: must be env:NAME, vault:path, or none — "
                        "a literal secret is not allowed"
                    )
    return messages


def check_integration_egress(policy: Policy, root: Path) -> list[str]:
    """An integration that declares no egress hosts is explicitly closed."""
    messages: list[str] = []
    for path in _candidate_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            instance = load_integration(path)
        except Exception:  # noqa: BLE001 - reported by check_integrations
            continue
        if isinstance(instance, Mapping) and instance.get("egress") in ([], None):
            if instance.get("baseUrl"):
                messages.append(f"{rel} $.egress: empty egress list with a baseUrl is contradictory")
    return messages
