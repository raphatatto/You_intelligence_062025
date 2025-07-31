from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from uuid import uuid4

from packages.database.session import get_session
from packages.jobs.download.download_gdb import baixar_gdb  # 🚨 precisa estar implementado corretamente
from apps.api.services import admin_service

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


# ----------------------
# ⬇️ DOWNLOAD DE GDB
# ----------------------

class DownloadPayload(BaseModel):
    distribuidora: str
    ano: int

@router.post("/v1/admin/download")
async def download_dataset(payload: DownloadPayload):
    try:
        baixar_gdb(payload.distribuidora, payload.ano)
        return {"status": "ok", "mensagem": "Download iniciado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/admin/download/status")
async def status_download(distribuidora: str, ano: int, db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT status, tempo_download, erro, updated_at
        FROM intel_lead.download_log
        WHERE distribuidora = :dist AND ano = :ano
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    result = await db.execute(query, {"dist": distribuidora, "ano": ano})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Download não encontrado.")

    return {
        "status": row.status,
        "tempo_download": row.tempo_download,
        "erro": row.erro,
        "updated_at": row.updated_at
    }


@router.post("/dashboard/refresh")
async def atualizar_materializadas(db: AsyncSession = Depends(get_session)):
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.mv_lead_completo_detalhado"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_distribuidora"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_energia_municipio"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_ano_camada"))
    await db.commit()
    return {"status": "ok", "msg": "Materializadas atualizadas com sucesso"}
