from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.session import get_session
from packages.jobs.queue import enqueue
from apps.api.services import admin_service

router = APIRouter(prefix="/v1/admin", tags=["Admin"])

# ===== Schemas =====

class ImportacaoPayload(BaseModel):
    distribuidora: str
    ano: int
    # ex.: ["UCAT","UCMT","UCBT","PONNOT"]
    camadas: list[str] = ["UCBT", "PONNOT"]
    # opcional: URL direta caso queira forçar (senão buscamos no catálogo)
    url: str | None = None

class DownloadPayload(BaseModel):
    distribuidora: str
    ano: int

class EnrichPayload(BaseModel):
    lead_ids: list[str] | None = None


# ===== Importações / Downloads =====

@router.post("/importar")
async def importar(payload: ImportacaoPayload):
    """
    Enfileira (1) download do GDB e (2) importers selecionados.
    Retorna os IDs dos jobs para acompanhamento.
    """
    return await admin_service.executar_importacao(payload)

@router.post("/download")
async def download_dataset(payload: DownloadPayload):
    """
    Enfileira apenas o download (não bloqueia a requisição).
    """
    job_id = enqueue({
        "download": {
            "distribuidora": payload.distribuidora,
            "ano": payload.ano,
            "max_kbps": 256
        }
        # download-only: sem "script"
    }, priority=5)
    return {"status": "queued", "job_id": job_id}

@router.get("/download/status")
async def status_download(distribuidora: str, ano: int, db: AsyncSession = Depends(get_session)):
    """
    Último status do download em intel_lead.download_log.
    """
    q = text("""
        SELECT status, tempo_download, erro, updated_at
        FROM intel_lead.download_log
        WHERE distribuidora = :dist AND ano = :ano
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    rs = await db.execute(q, {"dist": distribuidora, "ano": ano})
    row = rs.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Download não encontrado.")
    return dict(row._mapping)


# ===== Métricas / Listagens rápidas =====

@router.get("/import-status")
async def listar_importacoes(db: AsyncSession = Depends(get_session)):
    """
    Mostra os últimos jobs da fila.
    """
    return await admin_service.listar_status_importacoes(db)

@router.get("/leads/status-count")
async def status_count(db: AsyncSession = Depends(get_session)):
    return await admin_service.contagem_por_status(db)

@router.get("/leads/distribuidoras-count")
async def count_por_distribuidora(db: AsyncSession = Depends(get_session)):
    return await admin_service.contagem_por_distribuidora(db)

@router.get("/leads/raw")
async def listar_leads_raw(db: AsyncSession = Depends(get_session)):
    return await admin_service.listar_leads_raw(db)


# ===== Enriquecimento (stubs seguros) =====

@router.post("/enriquecer")
async def enriquecer_tudo():
    return await admin_service.enriquecer_global()

@router.post("/enrich/geo")
async def enrich_google(payload: EnrichPayload):
    return await admin_service.enriquecer_google(payload)

@router.post("/enrich/cnpj")
async def enrich_cnpj(payload: EnrichPayload):
    return await admin_service.enriquecer_cnpj(payload)


# ===== Ops de banco (materializadas) =====

@router.post("/dashboard/refresh")
async def refresh_materializadas(db: AsyncSession = Depends(get_session)):
    return await admin_service.refresh_materializadas(db)
