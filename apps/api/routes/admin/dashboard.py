from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.database.session import get_session

router = APIRouter(prefix="/v1/admin/dashboard", tags=["admin-dashboard"])

@router.get("/resumo")
async def dashboard_resumo(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'enriched') AS enriched,
            COUNT(*) FILTER (WHERE status = 'partially_enriched') AS partially_enriched,
            COUNT(*) FILTER (WHERE status = 'failed') AS failed,
            COUNT(*) FILTER (WHERE status = 'raw') AS raw,
            COUNT(*) AS total_leads
        FROM plead.lead
    """)

    query_ucs = text("SELECT COUNT(*) FROM plead.unidade_consumidora")

    res = await db.execute(query)
    leads = res.fetchone()

    res2 = await db.execute(query_ucs)
    total_ucs = res2.scalar()

    return {
        "enriched": leads.enriched or 0,
        "partially_enriched": leads.partially_enriched or 0,
        "failed": leads.failed or 0,
        "raw": leads.raw or 0,
        "total_leads": leads.total_leads or 0,
        "total_ucs": total_ucs or 0
    }
