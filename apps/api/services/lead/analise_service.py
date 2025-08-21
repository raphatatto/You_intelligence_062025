from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.analise_schema import(analise)

async def get_analise (db: AsyncSession) -> analise | None:
    query = text(""" SELECT * FROM intel_lead.municipio """)

    result = await db.execute(query)
    return result