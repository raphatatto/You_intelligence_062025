from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn

class Settings(BaseSettings):
    api_name: str = "Youon Intelligence API"
    api_version: str = "0.1.0"
    postgres_dsn: PostgresDsn

    class Config:
        env_file = ".env"          # coloque PG_DSN=postgresql+asyncpg://user:pass@host:5432/db
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
