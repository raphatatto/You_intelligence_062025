# apps/api/routes/leads.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from packages.database.session import get_session
from apps.api.schemas.lead import LeadDetalhado  # novo schema com os campos da view

router = APIRouter()

@router.get("/leads", response_model=List[LeadDetalhado])
async def listar_leads(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT * FROM intel_lead.vw_lead_completo_detalhado
        LIMIT 100
    """)
    result = await db.execute(query)
    return result.mappings().all()
