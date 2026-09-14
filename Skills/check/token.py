import os

def token_has_scope(scope: str) -> bool:
    """Check if token has specific scope"""
    scopes_env = os.getenv("GITHUB_TOKEN_SCOPES", "")
    scopes = [s.strip().lower() for s in scopes_env.split(",")]
    return scope.lower() in scopes or f"{scope}:write".lower() in scopes

def get_granted_scopes():
    return {
        "contents": token_has_scope("contents"),
        "workflows": token_has_scope("workflows")
    }
