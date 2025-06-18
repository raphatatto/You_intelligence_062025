from functools import lru_cache
from urllib.parse import quote
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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
        if self.postgres_dsn:                # prioriza a DSN pronta, se existir
            return self.postgres_dsn
        # monta automaticamente usando as DB_*
        return (
            f"postgresql+asyncpg://{quote(self.db_user)}:{quote(self.db_pass)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
