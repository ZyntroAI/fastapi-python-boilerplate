"""Regression guard for the `app` package initializer.

`app/__init__.py` used to create a second FastAPI app and instrument it before
the object existed, plus import the never-existing `app.routes`. That made
`import app` raise and broke every test collection touching the package.

The package must stay import-light: the real application lives in
`app.main` (served as `app.main:app`). These checks are pure static analysis so
they run without any OAuth env or optional instrumentation packages.
"""
from __future__ import annotations

import ast
from pathlib import Path

INIT = Path(__file__).resolve().parent.parent / "app" / "__init__.py"

# Instrumentation is set up on the app in its lifespan, never at package import.
FORBIDDEN_IMPORTS = {"opentelemetry", "slowapi", "starlette"}


def _imported_roots(source: str) -> set[str]:
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


def test_package_init_exists():
    assert INIT.is_file(), "app/__init__.py must exist so `app` is a package"


def test_package_init_parses():
    """An unparsable initializer takes down every import of the package."""
    ast.parse(INIT.read_text(encoding="utf-8"))


def test_package_init_has_no_heavy_instrumentation():
    roots = _imported_roots(INIT.read_text(encoding="utf-8"))
    offenders = roots & FORBIDDEN_IMPORTS
    assert not offenders, (
        f"app/__init__.py must not import {offenders} — "
        "those are optional/instrumentation deps and belong in app.main's lifespan"
    )


def test_package_init_does_not_import_missing_routes_module():
    """`from app.routes import ...` referred to a module that has never existed."""
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    assert "app.routes" not in modules, (
        "app/__init__.py must not import app.routes (does not exist; routers live in app.api.*)"
    )


def test_package_init_does_not_construct_fastapi_app():
    """Two FastAPI apps in one package is the bug we are guarding against."""
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "FastAPI", (
                "app/__init__.py must not construct FastAPI — the app lives in app.main"
            )
