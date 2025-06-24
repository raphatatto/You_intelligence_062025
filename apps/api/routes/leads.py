# apps/api/routes/leads.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from packages.database.session import get_session
from apps.api.schemas.lead import LeadList, LeadBase, LeadDetail, LeadMapOut, LeadResumo
from apps.api.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])

@router.get("", response_model=LeadList)
async def list_leads(
    segment: str | None = Query(None, description="home, cni, gtd"),
    classe: str | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
):
    total, items = await lead_service.list_leads(db, segment, classe, skip, limit)
    return {"total": total, "items": items}

@router.get("/{lead_id}", response_model=LeadDetail)
async def lead_detail(
    lead_id: str,
    db: AsyncSession = Depends(get_session),
):
    lead = await lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.get("/heatmap", response_model=list[tuple[float, float, int]])
async def heatmap(
    segment: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    """
    Retorna tuplas (lat, lon, count) usadas diretamente pelo front
    para colocar círculos no mapa.
    """
    return await lead_service.heatmap_points(db, segment)

@router.get("/map/points", response_model=list[LeadMapOut])
async def get_lead_points(
    status: str | None = Query(None),
    distribuidora: str | None = Query(None),
    limit: int = Query(default=1000),
    db: AsyncSession = Depends(get_session),
):
    return await lead_service.get_map_points(db, status, distribuidora, limit)

@router.get("/resumo", response_model=LeadResumo)
async def resumo(
    estado: str | None = Query(None),
    municipio: str | None = Query(None),
    segmento: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    return await lead_service.get_resumo(db, estado, municipio, segmento)

@router.get("/raw", response_model=LeadList)
async def raw_leads(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_session),
):
    """
    Retorna total e os primeiros 'limit' leads brutos
    sem depender de colunas inexistentes no ORM.
    """
    # 1) Conta total de leads brutos
    total_res = await db.execute(text("SELECT count(*) FROM lead_bruto"))
    total = total_res.scalar_one()

    # 2) Busca os primeiros registros
    sql = """
        SELECT 
            id, nome_uc, cnpj, classe, subgrupo, modalidade, segmento,
            distribuidora, municipio_ibge, data_conexao, status
        FROM lead_bruto
        ORDER BY id
        LIMIT :limit
        OFFSET :skip
    """
    result = await db.execute(text(sql), {"limit": limit, "skip": skip})
    rows = result.fetchall()

    # 3) Mapeia cada linha no schema LeadBase
    items = [LeadBase(**r._mapping) for r in rows]

    return {"total": total, "items": items}
