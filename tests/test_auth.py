import pytest
import requests

from auth import refresh_access_token


class FakeResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json_data = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} Error", response=self
            )


def test_refresh_access_token_success(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 3600,
            },
            status_code=200,
        )

    monkeypatch.setattr(requests, "post", fake_post)

    result = refresh_access_token(
        url="https://example.com/token",
        refresh_token="old-refresh-token",
        client_id="my-client-id",
        client_secret="my-client-secret",
    )

    assert result["access_token"] == "new-access-token"
    assert result["refresh_token"] == "new-refresh-token"

    assert captured["url"] == "https://example.com/token"
    assert captured["json"] == {
        "grant_type": "refresh_token",
        "refresh_token": "old-refresh-token",
        "client_id": "my-client-id",
        "client_secret": "my-client-secret",
    }
    assert captured["timeout"] == 10.0


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 403, 500],
)
def test_refresh_access_token_http_error(monkeypatch, status_code):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(
            {"error": "invalid_grant"},
            status_code=status_code,
        )

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(requests.HTTPError):
        refresh_access_token(
            url="https://example.com/token",
            refresh_token="bad-token",
            client_id="client",
            client_secret="secret",
        )


def test_refresh_access_token_network_error(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        raise requests.ConnectionError("Network unavailable")

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(requests.ConnectionError):
        refresh_access_token(
            url="https://example.com/token",
            refresh_token="token",
            client_id="client",
            client_secret="secret",
        )


def test_refresh_access_token_invalid_json(monkeypatch):
    class InvalidJsonResponse(FakeResponse):
        def json(self):
            raise ValueError("Response is not valid JSON")

    def fake_post(url, json=None, timeout=None):
        return InvalidJsonResponse(status_code=200)

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(ValueError, match="not valid JSON"):
        refresh_access_token(
            url="https://example.com/token",
            refresh_token="token",
            client_id="client",
            client_secret="secret",
        )