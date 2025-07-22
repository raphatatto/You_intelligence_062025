# admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import uuid4
from packages.database.session import get_session
from . import admin_service

router = APIRouter()

# ----------------------
# 📦 IMPORTAÇÕES
# ----------------------

class ImportacaoPayload(BaseModel):
    distribuidora: str
    prefixo: str
    ano: int
    url: str
    camadas: list[str]  # ["UCAT", "UCMT", "UCBT"]

@router.get("/v1/import-status")
async def listar_importacoes(db: AsyncSession = Depends(get_session)):
    return await admin_service.listar_status_importacoes(db)

@router.post("/v1/importar")
async def rodar_importacao(payload: ImportacaoPayload):
    return await admin_service.executar_importacao(payload)


# ----------------------
# 🧠 ENRIQUECIMENTO GLOBAL
# ----------------------

@router.post("/v1/enriquecer")
async def enrich_all():
    return await admin_service.enriquecer_global()


# ----------------------
# 🧠 ENRIQUECIMENTO SELETIVO
# ----------------------

class EnrichPayload(BaseModel):
    lead_ids: list[str]

@router.post("/v1/admin/enrich/geo")
async def enrich_google(payload: EnrichPayload):
    return await admin_service.enriquecer_google(payload)

@router.post("/v1/admin/enrich/cnpj")
async def enrich_cnpj(payload: EnrichPayload):
    return await admin_service.enriquecer_cnpj(payload)


# ----------------------
# 📊 DASHBOARD / MÉTRICAS
# ----------------------

@router.get("/v1/leads/status-count")
async def status_count(db: AsyncSession = Depends(get_session)):
    return await admin_service.contagem_por_status(db)

@router.get("/v1/leads/distribuidoras-count")
async def count_por_distribuidora(db: AsyncSession = Depends(get_session)):
    return await admin_service.contagem_por_distribuidora(db)


# ----------------------
# 🗃️ LEADS RAW
# ----------------------

@router.get("/v1/admin/leads/raw")
async def listar_leads_raw(db: AsyncSession = Depends(get_session)):
    return await admin_service.listar_leads_raw(db)