from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.database.session import get_session

router = APIRouter(prefix="/v1/admin/leads", tags=["admin-leads"])


# 🔹 Endpoint antigo: lista 100 leads brutos
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


# 🔹 NOVO: resumo geral por status
@router.get("/resumo")
async def resumo_leads(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT
            SUM(CASE WHEN status = 'raw' THEN 1 ELSE 0 END) AS raw,
            SUM(CASE WHEN status = 'parcialmente_enriquecido' THEN 1 ELSE 0 END) AS parcialmente_enriquecido,
            SUM(CASE WHEN status = 'enriquecido' THEN 1 ELSE 0 END) AS enriquecido,
            SUM(CASE WHEN status = 'falha_enriquecer' THEN 1 ELSE 0 END) AS falha_enriquecer
        FROM intel_lead.vw_lead_status_enriquecimento
    """)
    res = await db.execute(query)
    return dict(res.fetchone())


# 🔹 NOVO: total por distribuidora
@router.get("/distribuidora")
async def leads_por_distribuidora(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT distribuidora, COUNT(*) AS total_leads
        FROM intel_lead.resumo_leads_distribuidora
        GROUP BY distribuidora
        ORDER BY total_leads DESC
    """)
    res = await db.execute(query)
    return [dict(r) for r in res.fetchall()]


# 🔹 NOVO: evolução por ano/camada
@router.get("/ano-camada")
async def leads_por_ano_camada(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT
            ano,
            SUM(CASE WHEN camada = 'UCAT' THEN total ELSE 0 END) AS UCAT,
            SUM(CASE WHEN camada = 'UCMT' THEN total ELSE 0 END) AS UCMT,
            SUM(CASE WHEN camada = 'UCBT' THEN total ELSE 0 END) AS UCBT
        FROM intel_lead.resumo_leads_ano_camada
        GROUP BY ano
        ORDER BY ano
    """)
    res = await db.execute(query)
    return [dict(r) for r in res.fetchall()]
