from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.database.session import get_session

router = APIRouter(prefix="/v1/admin/leads", tags=["admin-leads"])


@router.get("/raw")
async def listar_leads_raw(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            id,
            id_interno,
            bairro,
            cep,
            municipio_ibge,
            distribuidora,
            status,
            latitude,
            longitude
        FROM plead.lead
        WHERE status = 'raw'
        ORDER BY ultima_atualizacao DESC
        LIMIT 100
    """)
    res = await db.execute(query)
    return [dict(row) for row in res.fetchall()]
