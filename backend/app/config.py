"""
Application configuration management using Pydantic BaseSettings.

Responsibilities:
- Load configuration from environment variables and .env file
- Provide strongly-typed, validated settings
- Centralize environment-specific values (DB, JWT, CORS, Redis)

QE relevance:
- Enables consistent behavior across local, QA, and prod
- Reduces configuration-related defects
- Makes test environments reproducible
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Priority order:
    1. OS environment variables
    2. .env file (for local development)

    QE/SIT notes:
    - Strong typing catches misconfiguration early
    - Missing required variables fail fast at startup
    """

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # -------------------------------------------------
    # Core environment configuration
    # -------------------------------------------------
    APP_ENV: str = "local"  # local | qa | prod

    # -------------------------------------------------
    # Database configuration
    # -------------------------------------------------
    DATABASE_URL: str  # required; app fails to start if missing

    # -------------------------------------------------
    # Authentication / security
    # -------------------------------------------------
    JWT_SECRET: str            # required secret key
    JWT_EXPIRE_MIN: int = 120  # token lifetime in minutes

    # -------------------------------------------------
    # Optional integrations
    # -------------------------------------------------
    REDIS_URL: Optional[str] = None  # worker / async processing

    # -------------------------------------------------
    # CORS configuration
    # -------------------------------------------------
    # Comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3000"

    def cors_list(self) -> List[str]:
        """
        Convert comma-separated CORS_ORIGINS string into a list.

        Example:
            "http://localhost:3000,https://qa-ui.example.com"
            -> ["http://localhost:3000", "https://qa-ui.example.com"]

        QE relevance:
        - Enables environment-specific UI/API integration
        - Prevents accidental over-permissive CORS in production
        """
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


# Singleton settings instance used throughout the app
settings = Settings()


