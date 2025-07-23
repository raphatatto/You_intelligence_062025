from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from packages.database.session import get_session
from apps.api.services.lead.geo_service import buscar_top_leads_geo
from apps.api.schemas.lead_schema import LeadGeoOut

router = APIRouter(prefix="/v1", tags=["leads"])

@router.get("/leads-geo", response_model=list[LeadGeoOut])
async def listar_leads_geo(limit: int = 300, db: AsyncSession = Depends(get_session)):
    return await buscar_top_leads_geo(db, limit)
