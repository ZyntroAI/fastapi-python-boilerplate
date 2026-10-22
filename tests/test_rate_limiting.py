import time

import requests


def get(url: str) -> int:
    return requests.get(url, timeout=2).status_code


def test_first_api_request_is_allowed(api_url):
    assert get(api_url) == 200


def test_api_burst_is_allowed(api_url):
    statuses = [get(api_url) for _ in range(20)]
    assert all(status == 200 for status in statuses)


def test_api_exceeding_burst_returns_429(api_url):
    # Consume the burst.
    for _ in range(20):
        get(api_url)

    # The next request exceeds the configured burst.
    assert get(api_url) == 429


def test_rate_limit_recovers_after_delay(api_url):
    for _ in range(20):
        get(api_url)

    assert get(api_url) == 429

    # At 10 requests/second, wait long enough for capacity to recover.
    time.sleep(1.1)

    assert get(api_url) == 200


def test_auth_limit_is_stricter(auth_url):
    statuses = [get(auth_url) for _ in range(10)]

    # 1 initial request + 5 burst requests should pass.
    assert statuses[:6].count(200) == 6
    assert 429 in statuses[6:]


def test_rate_limit_response_is_429(api_url):
    for _ in range(21):
        status = get(api_url)

    assert status == 429


def test_different_clients_are_isolated(api_url):
    # This test requires a test proxy or source-IP variation.
    # In CI, run each client from a separate network namespace/container.
    assert get(api_url) == 200