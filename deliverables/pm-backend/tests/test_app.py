"""Tests for the integrated PM backend.

Runs with encryption disabled (default) and, in a subprocess, with
ENCRYPT_AT_REST=true to prove the opt-in path selects an encrypted column.
"""
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main, pm_csv


@pytest.fixture(scope="module")
def client():
    # A context-managed TestClient fires the app's lifespan/startup handler,
    # which runs init_db() so the program tables exist.
    with TestClient(main.app) as c:
        yield c


# --------------------------------------------------------------------------
# Health + tool switcher
# --------------------------------------------------------------------------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "active_tool" in body


def test_tool_list_default(client):
    r = client.get("/api/tool")
    assert r.status_code == 200
    body = r.json()
    assert "active_tool" in body
    assert set(body["tools"]) == {"pm_csv", "billing", "settings"}


def test_tool_switch_roundtrip(client):
    r = client.post("/api/tool", json={"tool": "billing"})
    assert r.status_code == 200
    assert r.json()["active_tool"] == "billing"
    # restore
    client.post("/api/tool", json={"tool": "pm_csv"})


def test_tool_switch_unknown(client):
    r = client.post("/api/tool", json={"tool": "nope"})
    assert r.status_code == 400


# --------------------------------------------------------------------------
# PM CSV
# --------------------------------------------------------------------------

def test_template_endpoint(client):
    r = client.get("/api/csv/template")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    text = r.text
    assert "program_id" in text and "name" in text and "owner" in text


def test_rows_to_csv_roundtrip():
    rows = [
        {"name": "Alpha", "owner": "A", "status": "active", "budget": 1000},
        {"name": "Beta", "status": "planned", "risk": "med"},
    ]
    csv_text = pm_csv.rows_to_csv(rows)
    parsed = pm_csv.parse_csv(csv_text)
    assert [p.name for p in parsed] == ["Alpha", "Beta"]
    assert parsed[0].budget == 1000
    assert parsed[0].status == "active"


def test_generate_endpoint(client):
    r = client.post(
        "/api/csv/generate",
        json={"rows": [{"name": "X", "status": "active"}]},
    )
    assert r.status_code == 200
    assert r.json()["count"] == 1


def test_validate_reports_bad_status(client):
    r = client.post(
        "/api/csv/validate",
        json={"rows": [{"name": "X", "status": "not-a-status"}]},
    )
    body = r.json()
    assert body["valid"] is False
    assert body["errors"]


# --------------------------------------------------------------------------
# Billing (stub provider)
# --------------------------------------------------------------------------

def test_billing_provider_info(client):
    r = client.get("/api/billing/provider")
    assert r.status_code == 200
    assert r.json()["provider"] == "stub"


def test_billing_customer_invoice_charge_flow(client):
    c = client.post(
        "/api/billing/customers", json={"email": "a@b.com", "name": "A"}
    ).json()
    assert c["id"].startswith("cus_")
    inv = client.post(
        "/api/billing/invoices",
        json={"customer_id": c["id"], "amount": 2500, "currency": "usd"},
    ).json()
    assert inv["amount"] == 2500 and inv["status"] == "open"
    pi = client.post(
        "/api/billing/charges",
        json={"customer_id": c["id"], "amount": 2500, "currency": "usd"},
    ).json()
    assert pi["status"] == "succeeded"


def test_billing_unknown_customer_404(client):
    r = client.post(
        "/api/billing/invoices",
        json={"customer_id": "missing", "amount": 100},
    )
    assert r.status_code == 404


# --------------------------------------------------------------------------
# Program registry (exercises optional encryption on 'note')
# --------------------------------------------------------------------------

def test_program_create_list_get(client):
    created = client.post(
        "/api/programs",
        json={"name": "Launch", "owner": "Nattapong", "note": "secret value"},
    ).json()
    pid = created["id"]
    assert created["note"] == "secret value"
    listed = client.get("/api/programs").json()
    assert any(p["id"] == pid for p in listed)
    fetched = client.get(f"/api/programs/{pid}").json()
    assert fetched["note"] == "secret value"


# --------------------------------------------------------------------------
# Encryption at rest round-trip in a clean subprocess
# --------------------------------------------------------------------------

def test_encrypt_at_rest_stores_ciphertext():
    """With ENCRYPT_AT_REST=true the note column is an EncryptedString type and
    a Fernet instance is active (ciphertext on disk, decrypted on read)."""
    result = subprocess.run(
        [sys.executable, "-c", (
            "import os; os.environ['ENCRYPT_AT_REST']='true';"
            "os.environ['ENCRYPTION_SECRET']='test-secret';"
            "os.environ['DATABASE_URL']='sqlite:///:memory:';"
            "from app import db;"
            "col=db.ProgramRecord.__table__.c.note;"
            "print(type(col.type).__name__);"
            "print('encrypted' if db._fernet is not None else 'plain')"
        )],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout.strip().splitlines()
    assert out[0] == "EncryptedString"
    assert out[1] == "encrypted"
