from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "OAuth FastAPI"
    APP_VERSION: str = "1.0.0"

    ENV: Literal[
        "dev",
        "development",
        "test",
        "staging",
        "prod",
        "production",
    ] = "dev"

    DEBUG: bool = False

    # Server
    ROOT_PATH: str = ""
    BASE_URL: AnyHttpUrl

    # Database
    DATABASE_URL: str
    DATABASE_URL_TEST: str | None = None

    # CORS
    CORS_ORIGINS: str = ""
    FRONTEND_ORIGIN: AnyHttpUrl | None = None

    # OAuth
    OAUTH_PROVIDER: str = "google"
    CLIENT_ID: str
    CLIENT_SECRET: SecretStr
    OAUTH_SCOPES: str = "openid email profile"
    OAUTH_CALLBACK_PATH: str = "/api/auth/callback"

    # JWT
    JWT_SECRET: SecretStr
    JWT_ALG: str = "HS256"

    JWT_TTL_SECONDS: int = Field(
        default=3600,
        ge=60,
        le=86400,
    )
    JWT_ISSUER: str | None = None
JWT_AUDIENCE: str | None = None

    # OAuth state
    SESSION_STATE_TTL_SECONDS: int = Field(
        default=600,
        ge=60,
        le=3600,
    )

    # Observability
    METRICS_ENABLED: bool = True
    ENABLE_REQUEST_LOGS: bool = True

    LOG_LEVEL: str = "INFO"

    @property
    def IS_PROD(self) -> bool:
        return self.ENV in {
            "prod",
            "production",
        }

    @property
    def IS_DEV(self) -> bool:
        return self.ENV in {
            "dev",
            "development",
        }

    @property
    def OAUTH_CALLBACK_URL(self) -> str:
        return (
            f"{str(self.BASE_URL).rstrip('/')}"
            f"{self.OAUTH_CALLBACK_PATH}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
