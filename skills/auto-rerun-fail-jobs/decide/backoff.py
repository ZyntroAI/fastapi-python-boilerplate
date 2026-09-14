def calculate_delay(attempt: int, initial_sec: int = 30, max_sec: int = 300) -> int:
    """delay = min(initial × 2^(attempt-1), max_sec)
    Attempt 1 → 30s
    Attempt 2 → 60s
    Attempt 3 → 120s
    """
    delay = initial_sec * (2 ** (attempt - 1))
    return min(delay, max_sec)


def next_retry_at(attempt: int) -> str:
    from datetime import datetime, timedelta
    delay = calculate_delay(attempt)
    return (datetime.utcnow() + timedelta(seconds=delay)).isoformat() + "Z"
