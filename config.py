"""
Pydantic settings for FastAPI application.
Type-safe configuration with environment variable validation.
"""

from typing import Any, List, Optional
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    PostgresDsn,
    RedisDsn,
    validator,
    Field,
)
from pydantic.networks import HttpUrl
from pydantic.types import SecretStr

class Settings(BaseSettings):
    """Application settings with validation."""

    # Project metadata
    PROJECT_NAME: str = "FastAPI High-Performance Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A production-grade FastAPI service with async SQLAlchemy, JWT auth, and observability"

    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    PRODUCTION: bool = Field(default=False, env="PRODUCTION")

    # Database
    DATABASE_URL: PostgresDsn = Field(
        ...,
        env="DATABASE_URL",
        description="PostgreSQL async connection string",
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    DATABASE_TIMEOUT: int = Field(default=5, env="DATABASE_TIMEOUT")

    # Redis
    REDIS_URL: RedisDsn = Field(
        ...,
        env="REDIS_URL",
        description="Redis connection string",
    )
    REDIS_CACHE_TTL: int = Field(default=300, env="REDIS_CACHE_TTL")  # 5 minutes

    # JWT Authentication
    JWT_SECRET_KEY: SecretStr = Field(
        ...,
        env="JWT_SECRET_KEY",
        description="JWT secret key for signing tokens",
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    CORS_ALLOW_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000"],
        env="CORS_ALLOW_ORIGINS",
        description="List of allowed origins for CORS",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_METHODS",
        description="Allowed HTTP methods for CORS",
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS",
        description="Allowed HTTP headers for CORS",
    )

    # Security
    TRUSTED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="TRUSTED_HOSTS",
        description="List of trusted hosts for security middleware",
    )
    SECURE_COOKIES: bool = Field(default=True, env="SECURE_COOKIES")
    CSRF_PROTECTION: bool = Field(default=True, env="CSRF_PROTECTION")

    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[HttpUrl] = Field(
        default=None,
        env="OTEL_EXPORTER_OTLP_ENDPOINT",
        description="OpenTelemetry collector endpoint",
    )
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, env="OTEL_EXPORTER_OTLP_INSECURE")

    # Rate Limiting
    RATE_LIMIT: str = Field(default="100/minute", env="RATE_LIMIT")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # External Services
    EXTERNAL_API_TIMEOUT: int = Field(default=5, env="EXTERNAL_API_TIMEOUT")

    @validator("CORS_ALLOW_ORIGINS")
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("TRUSTED_HOSTS")
    def parse_trusted_hosts(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Initialize settings
settings = Settings()
