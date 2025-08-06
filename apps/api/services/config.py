# apps/api/services/config.py
from functools import lru_cache
from urllib.parse import quote
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    db_port: int = 5432

    # opcionais
    db_schema: str | None = "intel_lead"
    db_sslmode: str | None = None  # ex: "require"
    postgres_dsn: str | None = None

    api_name: str = "Youon Intelligence API"
    api_version: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


    @property
    def dsn(self) -> str:
        if self.postgres_dsn:
            return self.postgres_dsn
        user = quote(self.db_user)
        pwd  = quote(self.db_pass)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
