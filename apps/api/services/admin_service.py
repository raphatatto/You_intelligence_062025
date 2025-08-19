from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.jobs.queue import enqueue

# Caminhos dos importers (iguais aos que usamos no orquestrador)
IMPORTERS = {
    "UCAT":   "packages/jobs/importers/importer_ucat_job.py",
    "UCMT":   "packages/jobs/importers/importer_ucmt_job.py",
    "UCBT":   "packages/jobs/importers/importer_ucbt_job.py",
    "PONNOT": "packages/jobs/importers/importer_ponnot_job.py",
}

class ImportacaoPayload(BaseModel):
    distribuidora: str
    ano: int
    camadas: list[str]
    url: str | None = None

# ============== Import / Download orchestration (enfileira) ==============

async def executar_importacao(payload: ImportacaoPayload) -> dict[str, Any]:
    dist = payload.distribuidora
    ano = int(payload.ano)
    gdb_name = f"{dist}_{ano}"
    gdb_path = f"data/downloads/{gdb_name}.gdb"

    # 1) Download job (worker resolve URL via catálogo; se você quiser forçar, passe url=...)
    download_job = enqueue({
        "download": {
            "distribuidora": dist,
            "ano": ano,
            "max_kbps": 256,
            # "url": payload.url,  # descomente para forçar URL específica
            "nome_destino": gdb_name,
        }
    }, priority=5)

    # 2) Importers selecionados
    job_ids: list[str] = []
    for camada in payload.camadas:
        cam = camada.upper().strip()
        script = IMPORTERS.get(cam)
        if not script:
            continue

        env = {}
        if cam == "UCBT":
            env.update({
                "UCBT_CHUNK_SIZE": "3000",
                "UCBT_ROWS_PER_COPY": "15000",
                "UCBT_SLEEP_MS_BETWEEN": "120",
            })
        if cam == "PONNOT":
            env.update({
                "PONNOT_CHUNK_SIZE": "4000",
                "PONNOT_SLEEP_MS_BETWEEN": "80",
            })

        job_id = enqueue({
            "script": script,
            "args": ["--gdb", gdb_path, "--distribuidora", dist, "--ano", str(ano)],
            "env": env,
        }, priority=5)
        job_ids.append(job_id)

    return {
        "status": "queued",
        "download_job": download_job,
        "import_jobs": job_ids,
    }

# ============== Métricas / Listagens rápidas ==============

async def listar_status_importacoes(db: AsyncSession):
    q = text("""
        SELECT id, status, tries, priority, worker_id, created_at, started_at, finished_at,
               (payload->>'script') AS script,
               (payload->'download') IS NOT NULL AS has_download
        FROM import_queue
        ORDER BY created_at DESC
        LIMIT 100
    """)
    rs = await db.execute(q)
    return [dict(r._mapping) for r in rs.fetchall()]

async def contagem_por_status(db: AsyncSession):
    q = text("""
        SELECT COALESCE(situacao,'(null)') AS situacao, COUNT(*) AS qtde
        FROM intel_lead.lead_bruto
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 50
    """)
    rs = await db.execute(q)
    return [dict(r._mapping) for r in rs.fetchall()]

async def contagem_por_distribuidora(db: AsyncSession):
    q = text("""
        SELECT COALESCE(distribuidora_id::text,'(null)') AS distribuidora_id, COUNT(*) AS qtde
        FROM intel_lead.lead_bruto
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 100
    """)
    rs = await db.execute(q)
    return [dict(r._mapping) for r in rs.fetchall()]

async def listar_leads_raw(db: AsyncSession):
    q = text("""
        SELECT id, uc_id, distribuidora_id, ano, origem, cnae, municipio_id, bairro, cep
        FROM intel_lead.lead_bruto
        ORDER BY id DESC
        LIMIT 200
    """)
    rs = await db.execute(q)
    return [dict(r._mapping) for r in rs.fetchall()]

# ============== Enriquecimentos (stubs seguros) ==============

async def enriquecer_global():
    # aqui você pode enfileirar pipelines de enriquecimento, se quiser
    return {"status": "queued", "message": "pipeline de enriquecimento global ainda não configurado"}

async def enriquecer_google(payload):
    return {"status": "queued", "message": "enriquecimento GEO ainda não configurado", "lead_ids": payload.lead_ids}

async def enriquecer_cnpj(payload):
    return {"status": "queued", "message": "enriquecimento CNPJ ainda não configurado", "lead_ids": payload.lead_ids}

# ============== Ops de banco ==============

async def refresh_materializadas(db: AsyncSession):
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.mv_lead_completo_detalhado"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_distribuidora"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_energia_municipio"))
    await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_ano_camada"))
    await db.commit()
    return {"status": "ok", "msg": "Materializadas atualizadas com sucesso"}
