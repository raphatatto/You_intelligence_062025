# packages/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from apps.api.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.dsn,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
