from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4
from apps.api.schemas.lead_schema import ImportStatusOut
from packages.jobs.download.download_gdb import baixar_gdb
from packages.orquestrator.orquestrador_job import orquestrar_importacao
from packages.jobs.enrichers.enrich_geo_job import enrich_geo_info
from packages.jobs.enrichers.enrich_cnpj_job import enrich_cnpj
from packages.jobs.enrichers.pipeline import rodar_pipeline_enriquecimento


# 🔍 Listar status das importações
async def listar_status_importacoes(db: AsyncSession) -> list[ImportStatusOut]:
    query = text("""
        SELECT distribuidora, ano, camada, status, data_execucao
        FROM intel_lead.import_status
        ORDER BY data_execucao DESC
        LIMIT 100
    """)
    result = await db.execute(query)
    rows = result.mappings().all()
    return [ImportStatusOut(**dict(r)) for r in rows]


# 🚀 Executar importação completa (GDB já existente ou baixado antes)
async def executar_importacao(payload):
    import_id = str(uuid4())

    # Orquestrar com as camadas corretas
    orquestrar_importacao(
        distribuidora=payload.distribuidora,
        prefixo=payload.prefixo,
        ano=payload.ano,
        url=payload.url,
        camadas=payload.camadas,
        import_id=import_id
    )

    return {"status": "ok", "import_id": import_id}


# 🧠 Enriquecimento global (tudo que estiver com status 'raw')
async def enriquecer_global():
    return rodar_pipeline_enriquecimento()


# 🧠 Enriquecimento por coordenadas
async def enriquecer_google(payload):
    return enrich_geo_info(payload.lead_ids)


# 🧠 Enriquecimento por CNPJ
async def enriquecer_cnpj(payload):
    return enrich_cnpj(payload.lead_ids)


# 📊 Contagem de leads por status
async def contagem_por_status(db: AsyncSession):
    query = text("""
        SELECT status, COUNT(*) AS total
        FROM intel_lead.lead_bruto
        GROUP BY status
    """)
    result = await db.execute(query)
    return [{"status": row.status, "total": row.total} for row in result]


# 📊 Contagem por distribuidora
async def contagem_por_distribuidora(db: AsyncSession):
    query = text("""
        SELECT distribuidora_id, COUNT(*) AS total
        FROM intel_lead.lead_bruto
        GROUP BY distribuidora_id
    """)
    result = await db.execute(query)
    return [{"distribuidora": row.distribuidora_id, "total": row.total} for row in result]


# 📦 Leads brutos com status = raw (admin visual)
async def listar_leads_raw(db: AsyncSession):
    query = text("""
        SELECT 
            uc_id, bairro, cep, municipio_id, distribuidora_id,
            status, latitude, longitude
        FROM intel_lead.lead_bruto
        WHERE status = 'raw'
        ORDER BY import_id DESC
        LIMIT 100
    """)
    result = await db.execute(query)
    return [dict(row) for row in result.fetchall()]
