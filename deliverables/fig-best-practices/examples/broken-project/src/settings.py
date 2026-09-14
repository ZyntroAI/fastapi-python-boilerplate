"""Broken example — a credential assigned to a literal.

The value below is a fixture, not a live key, but it has the shape of one so
the SECURITY criterion has something real to catch. The gate redacts it.
"""

# The scanner flags the assignment on the next line.
SERVICE_TOKEN = "abcdef1234567890abcdef1234567890"


def get_token() -> str:
    return SERVICE_TOKEN
