import os

def get_installation_scopes():
    """Read permissions from token/env"""
    token = os.getenv("GITHUB_TOKEN", "")
    # Simulate scope decode — real impl uses /user or app JWT
    scopes = os.getenv("GITHUB_TOKEN_SCOPES", "").split(",")
    return [s.strip() for s in scopes if s.strip()]
