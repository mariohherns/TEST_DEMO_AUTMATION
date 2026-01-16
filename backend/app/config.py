from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "local"
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MIN: int = 120
    REDIS_URL: Optional[str] = None
    CORS_ORIGINS: str = "http://localhost:3000"

    def cors_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()

