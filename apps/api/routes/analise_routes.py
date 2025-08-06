from apps.api.schemas.analise_schema import(analise)
from apps.api.services.lead.analise_service import( get_analise)
from packages.database.session import get_session
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analise", tags=["analise"])

@router.get("/mercado", response_model=List[analise])
async def listar_muncipios(
    db:AsyncSession = Depends(get_session),
):
    rows = await get_analise(db)
    return [analise.model_validate(r, from_attributes=True) for r in rows]
