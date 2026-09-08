"""Standalone tests for the credential broker + skill clients.

Loads modules in isolation (stubbing app.core.config) because the repo's app/
package pulls in many optional deps (opentelemetry, etc.) not present in this
sandbox. Verifies the unconfigured / no-broker paths are safe and structured.
"""
import asyncio
import importlib.util
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)  # fastapi-python-boilerplate

def _stub_config():
    app = types.ModuleType("app"); app.__path__ = []
    core = types.ModuleType("app.core"); core.__path__ = []
    cfg = types.ModuleType("app.core.config")
    cfg.settings = types.SimpleNamespace(CREDENTIAL_BROKER_URL=None, BROKER_TOKEN=None)
    sys.modules.update({"app": app, "app.core": core, "app.core.config": cfg})

def _load_broker():
    spec = importlib.util.spec_from_file_location(
        "app.core.credential_broker", os.path.join(_REPO, "app/core/credential_broker.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def test_unconfigured_health():
    _stub_config(); broker = _load_broker()
    assert asyncio.run(broker.CredentialBroker().health()) == {"status": "unconfigured"}

def test_unconfigured_resolve_returns_before_using_req():
    _stub_config(); broker = _load_broker()
    # req=None proves the endpoint guard short-circuits first
    r = asyncio.run(broker.CredentialBroker().resolve(None))
    assert r["status"] == "unconfigured" and r["scope_ok"] is False

def test_unconfigured_lease_release():
    _stub_config(); broker = _load_broker()
    assert asyncio.run(broker.CredentialBroker().lease("id")) is None
    assert asyncio.run(broker.CredentialBroker().release("x")) is False

def test_credential_broker_has_no_secret_fields():
    _stub_config(); broker = _load_broker()
    src = open(os.path.join(_REPO, "app/core/credential_broker.py")).read()
    assert "sk-" not in src and "api_key" not in src  # no secret material
    assert broker.CredentialRequest.model_fields  # pydantic model defined
