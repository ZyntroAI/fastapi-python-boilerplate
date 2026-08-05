from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server / routing
    ROOT_PATH: str | None = None
    BASE_URL: AnyUrl

    # OAuth
    OAUTH_PROVIDER: str = "google"

    CLIENT_ID: str
    CLIENT_SECRET: str
    OAUTH_SCOPES: str = "openid email profile"

    # redirect path must match what provider expects
    OAUTH_CALLBACK_PATH: str = "/api/auth/callback"

    # token / jwt
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_TTL_SECONDS: int = 3600

    # security
    SESSION_STATE_TTL_SECONDS: int = 600

    # observability
    METRICS_ENABLED: bool = True

    # logging
    LOG_LEVEL: str = "INFO"

settings = Settings()
