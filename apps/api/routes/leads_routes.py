from fastapi import APIRouter, Depends, Query
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.lead_schema import (
    LeadDetalhado,
    LeadResumo,
    LeadQualidade,
    LeadMapOut,
    LeadList
)

from apps.api.services.lead.lead_service import (
    buscar_leads,
    get_lead,
    get_resumo,
    get_map_points,
    get_qualidade,
    heatmap_points
)

from packages.database.session import get_session

router = APIRouter(prefix="/v1/leads", tags=["leads"])

# 🔍 Listar leads com filtros e paginação
@router.get("/", response_model=LeadList)
async def listar_leads(
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    distribuidora: Optional[str] = None,
    segmento: Optional[str] = None,
    ordem: Optional[str] = "padrao",
    busca: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(300, ge=1, le=500),
    db: AsyncSession = Depends(get_session),
):
    return await buscar_leads(
        db=db,
        estado=estado,
        tipo=tipo,
        distribuidora=distribuidora,
        segmento=segmento,
        ordem=ordem,
        busca=busca,
        skip=skip,
        limit=limit,
    )


# 📋 Detalhamento de um lead específico
@router.get("/{uc_id}", response_model=LeadDetalhado)
async def detalhar_lead(
    uc_id: str,
    db: AsyncSession = Depends(get_session)
):
    return await get_lead(db, uc_id)


# 📊 Resumo estatístico de leads
@router.get("/resumo/estatisticas", response_model=LeadResumo)
async def resumo_leads(
    estado: Optional[str] = None,
    municipio: Optional[str] = None,
    segmento: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    return await get_resumo(db, estado, municipio, segmento)


# 📈 Qualidade DIC/FIC por lead
@router.get("/{uc_id}/qualidade", response_model=LeadQualidade)
async def qualidade_lead(
    uc_id: str,
    db: AsyncSession = Depends(get_session)
):
    return await get_qualidade(db, uc_id)


# 🗺️ Pontos para mapa
@router.get("/map", response_model=list[LeadMapOut])
async def pontos_mapa(
    status: Optional[str] = None,
    distribuidora: Optional[str] = None,
    limit: int = Query(500, ge=1, le=10000),
    db: AsyncSession = Depends(get_session),
):
    return await get_map_points(db, status, distribuidora, limit)


# 🔥 Heatmap de concentração
@router.get("/heatmap", response_model=list[tuple])
async def heatmap(
    segmento: Optional[str] = None,
    db: AsyncSession = Depends(get_session),
):
    return await heatmap_points(db, segmento)
