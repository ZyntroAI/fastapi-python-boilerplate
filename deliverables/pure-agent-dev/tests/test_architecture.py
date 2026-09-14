"""Guard the one rule of Issue #63.

    The Agent must never depend on the BytePlus SDK.
    api -> services -> agents -> providers.base -> adapter -> SDK

A comment cannot enforce that; this test can. It walks the import graph and
fails if any layer reaches across the interface.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "pure_agent"

# layer -> modules it is forbidden to import directly
FORBIDDEN = {
    "agents": {"pure_agent.providers.byteplus", "pure_agent.providers.mock"},
    "services": {"pure_agent.providers.byteplus", "pure_agent.providers.mock"},
    "schemas": {"pure_agent.providers", "pure_agent.agents", "pure_agent.services"},
}

CLOUD_SDKS = ("byteplus", "boto3", "botocore", "azure", "google.cloud")


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def layer_files(layer: str) -> list[Path]:
    return sorted(p for p in (PKG / layer).rglob("*.py"))


@pytest.mark.architecture
@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_does_not_import_across_the_interface(layer):
    banned = FORBIDDEN[layer]
    offenders = []
    for path in layer_files(layer):
        for module in imported_modules(path):
            if any(module == b or module.startswith(b + ".") for b in banned):
                offenders.append(f"{path.relative_to(ROOT)} imports {module}")
    assert not offenders, (
        f"{layer}/ must depend only on the provider *interface*, not an adapter:\n  "
        + "\n  ".join(offenders)
    )


@pytest.mark.architecture
def test_agents_never_reach_a_cloud_sdk():
    offenders = []
    for path in layer_files("agents"):
        source = path.read_text(encoding="utf-8").lower()
        for sdk in CLOUD_SDKS:
            if sdk in source:
                offenders.append(f"{path.relative_to(ROOT)} mentions {sdk}")
    assert not offenders, "agents/ must not reference a cloud SDK:\n  " + "\n  ".join(offenders)


@pytest.mark.architecture
def test_provider_implementation_is_imported_only_by_the_wiring_layer():
    """Only api/deps.py (and the adapter package itself) may name a concrete adapter."""
    allowed = {"pure_agent/api/deps.py", "pure_agent/providers/byteplus/__init__.py"}
    offenders = []
    for path in PKG.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        if rel in allowed or rel.startswith("pure_agent/providers/byteplus/"):
            continue
        for module in imported_modules(path):
            if module.startswith("pure_agent.providers.byteplus") or module == "pure_agent.providers.mock":
                offenders.append(f"{rel} imports {module}")
    assert not offenders, "concrete adapters must be wired in one place:\n  " + "\n  ".join(
        offenders
    )


@pytest.mark.architecture
def test_base_interface_is_the_only_provider_dependency_above_it():
    """agents/ + services/ may import providers.base and nothing else under providers/."""
    for layer in ("agents", "services"):
        for path in layer_files(layer):
            for module in imported_modules(path):
                if module.startswith("pure_agent.providers"):
                    assert module == "pure_agent.providers.base", (
                        f"{path.relative_to(ROOT)} imports {module}; "
                        "only pure_agent.providers.base is allowed here"
                    )
