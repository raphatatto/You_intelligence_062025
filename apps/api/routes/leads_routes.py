# apps/api/routes/leads_routes.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.lead_schema import (
    LeadDetalhadoOut
)
from apps.api.services.lead.lead_service import (
    get_lead,
    get_leads_detalhados,
)
from packages.database.session import get_session

router = APIRouter(prefix="/leads", tags=["leads"])

@router.get("/detalhados", response_model=List[LeadDetalhadoOut])
async def listar_leads_detalhados(
    limit: int = Query(300, ge=1, le=1000),
    db: AsyncSession = Depends(get_session),
):
    rows = await get_leads_detalhados(db, limit=limit)
    return [LeadDetalhadoOut.model_validate(r, from_attributes=True) for r in rows]

@router.get("/{uc_id}", response_model=LeadDetalhadoOut)
async def detalhar_lead(uc_id: str, db: AsyncSession = Depends(get_session)):
    lead = await get_lead(db, uc_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    # se get_lead já retornar dict, ok; se retornar ORM, valide:
    return LeadDetalhadoOut.model_validate(lead, from_attributes=True)
