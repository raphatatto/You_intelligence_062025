# api/services/config.py
from functools import lru_cache
from urllib.parse import quote
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    db_port: int = 5432

    db_schema: str  # ✅ Adiciona isso
    db_sslmode: str  # ✅ E isso também

    postgres_dsn: str | None = None

    api_name: str = "Youon Intelligence API"
    api_version: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # variáveis separadas (já existem no seu .env)
    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    db_port: int = 5432

    # opcional: se quiser continuar aceitando POSTGRES_DSN
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
        # escapa usuário e senha
        user = quote(self.db_user)
        pwd  = quote(self.db_pass)
        return (
            f"postgresql+asyncpg://{user}:{pwd}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
