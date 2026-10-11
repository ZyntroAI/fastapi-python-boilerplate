import requests


def refresh_access_token(
    url: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    timeout: float = 10.0,
) -> dict:
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()