from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "CRUD App"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./crud_app.db"

    # CORS
    allowed_origins: List[str] = ["http://localhost:8000"]

    @field_validator("database_url")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        allowed_schemes = (
            "sqlite+aiosqlite",
            "mysql+aiomysql",
        )
        if not any(v.startswith(s) for s in allowed_schemes):
            raise ValueError(
                f"DATABASE_URL must start with one of: {allowed_schemes}"
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
