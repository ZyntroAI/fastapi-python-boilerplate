from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ENV: str = "local"  # local | vercel | production
    
    # OAuth2 Provider (Google, GitHub, etc.)
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str | None = None  # PKCE ไม่ต้องใช้ secret บน client
    OAUTH_AUTHORIZE_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    OAUTH_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    OAUTH_USERINFO_URL: str = "https://openidconnect.googleapis.com/v1/userinfo"
    
    # Callback URL แยกตาม Environment
    @property
    def OAUTH_CALLBACK_URL(self) -> str:
        callbacks = {
            "local": "http://localhost:8000/auth/callback",
            "vercel": "https://your-app.vercel.app/auth/callback",
            "production": "https://api.example.com/auth/callback",
        }
        return callbacks.get(self.ENV, callbacks["local"])
    
    # Frontend redirect หลัง login สำเร็จ
    @property
    def FRONTEND_URL(self) -> str:
        urls = {
            "local": "http://localhost:3000",
            "vercel": "https://your-app.vercel.app",
            "production": "https://app.example.com",
        }
        return urls.get(self.ENV, urls["local"])
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [self.FRONTEND_URL]
    
    # JWT
    JWT_SECRET: str = "super-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # Redis (optional - for token storage)
    REDIS_URL: str | None = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
