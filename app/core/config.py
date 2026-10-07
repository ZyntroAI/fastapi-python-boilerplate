import os
# ─── Claude API ───
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
ANTHROPIC_VERSION: str = "2026-01-01"
HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "120"))
