"""Application configuration.

Read from environment variables so the same code runs in dev, staging, and
production without edits. Supports an optional ``.env`` file (no third-party
dependency required).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "Program Management Backend"
    version: str = "1.0.0"
    debug: bool = field(default_factory=lambda: _bool_env("DEBUG", False))

    # --- Database --------------------------------------------------------
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "sqlite:///./pm_backend.db"
        )
    )
    # Opt-in encryption at rest. The app never hard-depends on an encryption
    # library: when false, string fields are stored as plain text and the
    # cryptography package is never imported.
    encrypt_at_rest: bool = field(
        default_factory=lambda: _bool_env("ENCRYPT_AT_REST", False)
    )
    # Fernet key when encryption is enabled. Generate one with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # If unset, the app derives a stable key from ENCRYPTION_SECRET so it
    # still boots out of the box.
    encryption_key: str = field(
        default_factory=lambda: os.getenv("ENCRYPTION_KEY", "")
    )
    encryption_secret: str = field(
        default_factory=lambda: os.getenv("ENCRYPTION_SECRET", "change-me")
    )

    # --- Billing ---------------------------------------------------------
    # Provider-neutral interoperability. Only the selected provider's adapter
    # is required at runtime; the rest of the app talks to one interface.
    billing_provider: str = field(
        default_factory=lambda: os.getenv("BILLING_PROVIDER", "stub").lower()
    )
    billing_api_key: str = field(
        default_factory=lambda: os.getenv("BILLING_API_KEY", "")
    )
    billing_base_url: str = field(
        default_factory=lambda: os.getenv("BILLING_BASE_URL", "")
    )

    # --- Tool switcher ---------------------------------------------------
    active_tool: str = field(
        default_factory=lambda: os.getenv("ACTIVE_TOOL", "pm_csv").lower()
    )
    tools: tuple[str, ...] = ("pm_csv", "billing", "settings")


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader."""
    env_file = path or Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings()
