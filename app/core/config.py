from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "oauth-fastapi"
    environment: str = "development"

    oauth_client_id: str
    oauth_client_secret: str
    oauth_redirect_uri: str

    jwt_secret: str

    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
