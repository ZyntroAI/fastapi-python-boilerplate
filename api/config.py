from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Info
    api_title: str = "FastAPI Boilerplate API"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready FastAPI backend"
    
    # Server
    debug: bool = True

settings = Settings()
