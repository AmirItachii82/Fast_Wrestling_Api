"""
Core configuration settings for the Wrestling Dashboard API.

This module provides centralized configuration management using Pydantic Settings.
All configuration values can be overridden via environment variables.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Wrestling Dashboard API"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "change-this-in-production"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/wrestling_db"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/wrestling_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI Provider
    openai_api_key: Optional[str] = None
    ai_cache_ttl_hours: int = 24

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    ai_rate_limit_per_minute: int = 10

    # Sentry
    sentry_dsn: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: The application settings singleton.
    """
    return Settings()
