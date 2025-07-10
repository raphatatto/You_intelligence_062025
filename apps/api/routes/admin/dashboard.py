from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.database.session import get_session

router = APIRouter(prefix="/v1/admin/leads", tags=["admin-leads"])


@router.get("/raw")
async def listar_leads_raw(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            uc_id,
            bairro,
            cep,
            municipio_id,
            distribuidora_id,
            status,
            latitude,
            longitude
        FROM intel_lead.lead_bruto
        WHERE status = 'raw'
        ORDER BY import_id DESC
        LIMIT 100
    """)
    res = await db.execute(query)
    return [dict(row) for row in res.fetchall()]
