"""Tests: circuit breaker state machine"""
from app.circuit_breaker import CircuitBreaker


def test_closed_allows():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    assert cb.state == "CLOSED"
    assert cb.allow_request() is True


def test_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "CLOSED"
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.allow_request() is False


def test_success_resets_failures():
    cb = CircuitBreaker(failure_threshold=3, recovery_seconds=30)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    cb.record_failure()
    assert cb.state == "CLOSED"


def test_half_open_recovers_after_cooldown():
    cb = CircuitBreaker(failure_threshold=2, recovery_seconds=0.05)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    # หลัง cooldown → HALF_OPEN ปล่อย 1 request
    import time
    time.sleep(0.1)
    assert cb.state == "HALF_OPEN"
    assert cb.allow_request() is True


def test_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=1, recovery_seconds=0.05)
    cb.record_failure()
    assert cb.state == "OPEN"
    import time
    time.sleep(0.1)
    cb.record_failure()  # ใน HALF_OPEN ล้ม → OPEN อีก
    assert cb.state == "OPEN"
    assert cb.allow_request() is False
