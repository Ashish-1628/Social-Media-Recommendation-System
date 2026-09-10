from functools import lru_cache
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "GraphConnect API"
    DEBUG: bool = False

    # Database — defaults to local SQLite for zero-config dev
    DATABASE_URL: str = "sqlite:///./graphconnect.db"

    # JWT
    SECRET_KEY: str = "change-this-secret-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Redis (optional — leave blank to disable caching)
    REDIS_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
