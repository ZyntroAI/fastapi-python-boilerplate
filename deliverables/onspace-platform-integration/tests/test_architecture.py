"""Architecture guard — these tests fail if the layering regresses.

The service layer must stay callable from a worker, a CLI, or a GraphQL
resolver. That holds only while it imports nothing from FastAPI. These are
static source checks (no import games), so they are fast and deterministic.

If a rule here fails, the fix is to move the dependency down into the service
or up into the HTTP layer — never to relax this file.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "onspace"

# Modules that MUST NOT import an HTTP framework.
CORE_MODULES = [
    "cache.py",
    "circuit_breaker.py",
    "context.py",
    "fallback.py",
    "models.py",
    "service.py",
    "token_budget.py",
    "config.py",
    "factory.py",
]

# Modules allowed to know about HTTP.
HTTP_MODULES = ["api.py", "app.py", "middleware.py"]

HTTP_PREFIXES = ("fastapi", "starlette")


def _imported_roots(path: Path) -> set[str]:
    """Top-level module names imported by a file (via AST, not regex)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


@pytest.mark.parametrize("filename", CORE_MODULES)
def test_core_module_does_not_import_http_framework(filename):
    imported = _imported_roots(PKG / filename)
    offenders = {m for m in imported if m.startswith(HTTP_PREFIXES)}
    assert not offenders, f"{filename} must not import {offenders}"


def test_providers_do_not_import_http_framework():
    for path in (PKG / "providers").glob("*.py"):
        imported = _imported_roots(path)
        offenders = {m for m in imported if m.startswith(HTTP_PREFIXES)}
        assert not offenders, f"providers/{path.name} must not import {offenders}"


def _referenced_names(path: Path) -> set[str]:
    """Every identifier referenced in code (ignores docstrings/comments)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            names.add(node.func.id)
    return names


def test_service_constructs_nothing_http_specific():
    """A service that builds requests/responses is no longer transport-agnostic."""
    names = _referenced_names(PKG / "service.py")
    for forbidden in ["FastAPI", "APIRouter", "HTTPException", "Request", "JSONResponse"]:
        assert forbidden not in names, f"service.py must not reference {forbidden}"


def test_http_layer_is_thin():
    """The route must delegate — cache/budget/context logic belongs to the service."""
    names = _referenced_names(PKG / "api.py")
    for forbidden in ["TokenBudget", "cache_key", "compile_context", "FallbackRouter"]:
        assert forbidden not in names, f"api.py must not construct {forbidden}"


def test_http_modules_are_the_only_fastapi_importers():
    """Everything that imports FastAPI must be on the allow-list."""
    importers = set()
    for path in PKG.rglob("*.py"):
        if any(m.startswith(HTTP_PREFIXES) for m in _imported_roots(path)):
            importers.add(path.name)
    assert importers <= set(HTTP_MODULES), f"unexpected HTTP importers: {importers}"
