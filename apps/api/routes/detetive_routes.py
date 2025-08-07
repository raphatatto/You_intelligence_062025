# apps/api/routes/detetive_routes.py

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from packages.database.session import get_session
from packages.detectors.detetive_core import montar_dossie_detetive
from apps.api.schemas.lead_schema import DetetiveResponse 

router = APIRouter(prefix="/v1/detetive", tags=["Modo Detetive"])


@router.post("/analisar", response_model=DetetiveResponse)
async def analisar_dados_cliente(payload: dict, db: AsyncSession = Depends(get_session)):
    try:
        result = await asyncio.to_thread(montar_dossie_detetive, payload, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
