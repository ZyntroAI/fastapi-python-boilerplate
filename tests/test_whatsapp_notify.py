"""Tests for scripts/whatsapp_notify.py — config validation + API calls (mocked)."""
import os
import sys
from unittest import mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.whatsapp_notify import WhatsAppClient, WhatsAppConfigError

ENV = {
    "WHATSAPP_TOKEN": "test-token",
    "WHATSAPP_PHONE_ID": "1234567890",
    "WHATSAPP_API_VER": "v18.0",
}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)


def test_missing_config_raises(monkeypatch):
    monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
    with pytest.raises(WhatsAppConfigError):
        WhatsAppClient()


def test_non_digit_phone_id_raises(monkeypatch):
    monkeypatch.setenv("WHATSAPP_PHONE_ID", "abc-123")
    with pytest.raises(WhatsAppConfigError):
        WhatsAppClient()


def test_base_url_and_headers():
    c = WhatsAppClient()
    assert c.base_url == "https://graph.facebook.com/v18.0/1234567890"
    assert c.headers["Authorization"] == "Bearer test-token"


def test_test_connection_ok():
    c = WhatsAppClient()
    resp = mock.Mock(status_code=200)
    resp.json.return_value = {"id": "1234567890"}
    with mock.patch("scripts.whatsapp_notify.requests.get", return_value=resp) as g:
        ok, body = c.test_connection()
    assert ok is True and body["id"] == "1234567890"
    g.assert_called_once()


def test_test_connection_unsupported_get_request():
    """code=100 / subcode=33 should surface as not-ok, not raise."""
    c = WhatsAppClient()
    resp = mock.Mock(status_code=400)
    resp.json.return_value = {
        "error": {"message": "Unsupported get request", "code": 100, "error_subcode": 33}
    }
    with mock.patch("scripts.whatsapp_notify.requests.get", return_value=resp):
        ok, body = c.test_connection()
    assert ok is False
    assert body["error"]["error_subcode"] == 33


def test_test_connection_network_error():
    c = WhatsAppClient()
    import requests
    with mock.patch(
        "scripts.whatsapp_notify.requests.get",
        side_effect=requests.RequestException("boom"),
    ):
        ok, body = c.test_connection()
    assert ok is False and "boom" in body["error"]


def test_send_message_ok():
    c = WhatsAppClient()
    resp = mock.Mock(status_code=200)
    resp.raise_for_status = mock.Mock()
    resp.json.return_value = {"messages": [{"id": "wamid.ABC"}]}
    with mock.patch("scripts.whatsapp_notify.requests.post", return_value=resp) as p:
        ok, mid = c.send_message("66812345678", "hello")
    assert ok is True and mid == "wamid.ABC"
    # must POST to /messages with the required payload shape
    _, kwargs = p.call_args
    assert kwargs["json"]["messaging_product"] == "whatsapp"
    assert kwargs["json"]["to"] == "66812345678"
    assert p.call_args[0][0].endswith("/messages")


def test_send_message_empty_recipient():
    c = WhatsAppClient()
    ok, err = c.send_message("", "hi")
    assert ok is False and "empty" in err


def test_send_message_http_error():
    import requests
    c = WhatsAppClient()
    resp = mock.Mock(status_code=400)
    resp.text = '{"error":{"code":131008}}'
    err = requests.HTTPError(response=resp)
    with mock.patch("scripts.whatsapp_notify.requests.post", side_effect=err):
        ok, detail = c.send_message("66812345678", "hi")
    assert ok is False and "131008" in detail
