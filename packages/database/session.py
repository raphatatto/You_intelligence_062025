from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from apps.api.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.postgres_dsn, echo=False, pool_pre_ping=True)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False
)

from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
