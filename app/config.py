# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"

    # Origins loaded from env var or defaults per environment
    @property
    def allowed_origins(self) -> List[str]:
        if self.APP_ENV == "production":
            return [
                "https://your-production-domain.com",
                "https://fastapi-python-boilerplate-kappa-brown.vercel.app",
            ]
        elif self.APP_ENV == "staging":
            return [
                "https://staging.your-domain.com",
                "http://localhost:3000",
            ]
        else:
            # Development — allow localhost variants
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]

    class Config:
        env_file = ".env"


settings = Settings()
