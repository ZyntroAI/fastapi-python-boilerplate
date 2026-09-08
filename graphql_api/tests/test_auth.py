"""JWT auth unit tests."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.auth import AuthError, create_access_token, decode_token


def test_token_roundtrip():
    t = create_access_token({"sub": "1", "role": "admin"})
    payload = decode_token(t)
    assert payload["sub"] == "1"
    assert payload["role"] == "admin"


def test_decode_invalid_raises():
    with pytest.raises(AuthError):
        decode_token("not-a-jwt")
