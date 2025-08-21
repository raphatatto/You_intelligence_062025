from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.session import get_session

router = APIRouter(prefix="/v1/admin", tags=["Admin/DB"])

@router.post("/db/refresh")
async def refresh_materializadas(db: AsyncSession = Depends(get_session)):
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.mv_lead_completo_detalhado"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_distribuidora"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_energia_municipio"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_ano_camada"))
    await db.commit()
    return {"status": "ok"}

@router.get("/db/queue")
async def listar_fila(db: AsyncSession = Depends(get_session)):
    rs = await db.execute(text("""
        SELECT id, status, tries, priority, worker_id, created_at, started_at, finished_at,
               (payload->>'script') AS script
        FROM import_queue
        ORDER BY created_at DESC
        LIMIT 100
    """))
    return [dict(r._mapping) for r in rs.fetchall()]
