from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.lead import (
    LeadOut,
    LeadDetail,
    LeadMapOut,
    LeadResumo,
    LeadQualidade,
)

def parse_array_text(text: str | None) -> list[float] | None:
    if not text:
        return None
    try:
        return [float(x) for x in text.strip("{} ").split(",") if x]
    except Exception:
        return None

# 🔍 Listagem de leads (com view completa)
async def list_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = text("""
        SELECT *
        FROM intel_lead.vw_lead_com_cnae_desc
        ORDER BY nome_fantasia
        OFFSET :skip LIMIT :limit
    """)
    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.mappings().all()

    leads = []
    for row in rows:
        data = dict(row)
        dic_array = parse_array_text(data.get("dicMes"))
        fic_array = parse_array_text(data.get("ficMes"))
        data["dicMes"] = dic_array
        data["ficMes"] = fic_array
        data["dicMed"] = round(sum(dic_array) / len(dic_array), 2) if dic_array else None
        data["ficMed"] = round(sum(fic_array) / len(fic_array), 2) if fic_array else None
        leads.append(LeadOut(**data))

    total_query = text("SELECT COUNT(*) FROM intel_lead.lead_bruto")
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    return total, leads

# 📋 Detalhe completo de um lead
async def get_lead(db: AsyncSession, uc_id: str) -> LeadDetail | None:
    query = text("""
        SELECT *
        FROM intel_lead.vw_lead_com_cnae_desc
        WHERE uc_id = :uc_id
    """)
    result = await db.execute(query, {"uc_id": uc_id})
    row = result.mappings().first()
    if not row:
        return None

    data = dict(row)
    dic_array = parse_array_text(data.get("dicMes"))
    fic_array = parse_array_text(data.get("ficMes"))
    data["dicMes"] = dic_array
    data["ficMes"] = fic_array
    data["dicMed"] = round(sum(dic_array) / len(dic_array), 2) if dic_array else None
    data["ficMed"] = round(sum(fic_array) / len(fic_array), 2) if fic_array else None

    return LeadDetail(**data)

# 📈 Dados de qualidade de um lead (caso queira isolado)
async def get_qualidade(db: AsyncSession, uc_id: str) -> LeadQualidade | None:
    query = text("""
        SELECT dic, fic
        FROM intel_lead.lead_qualidade_mensal
        WHERE uc_id = :uc_id
    """)
    result = await db.execute(query, {"uc_id": uc_id})
    row = result.mappings().first()
    if not row:
        return None

    dic_array = parse_array_text(row["dic"])
    fic_array = parse_array_text(row["fic"])

    return LeadQualidade(
        dicMes=dic_array,
        ficMes=fic_array,
        dicMed=round(sum(dic_array) / len(dic_array), 2) if dic_array else None,
        ficMed=round(sum(fic_array) / len(fic_array), 2) if fic_array else None,
    )

# 🗺️ Pontos no mapa
async def get_map_points(db: AsyncSession, status: str | None, distribuidora: str | None, limit: int = 1000):
    query = text("""
        SELECT uc_id, latitude, longitude, classe, grupo_tensao, pac AS potencia, distribuidora_id AS distribuidora, status
        FROM intel_lead.lead_com_coordenadas
        WHERE (:status IS NULL OR status = :status)
          AND (:distribuidora IS NULL OR distribuidora_id = :distribuidora)
        LIMIT :limit
    """)
    result = await db.execute(query, {
        "status": status,
        "distribuidora": distribuidora,
        "limit": limit
    })
    return [LeadMapOut(**row._mapping) for row in result]

# 🔥 Heatmap (peso = número de UCs por coordenada)
async def heatmap_points(db: AsyncSession, segmento: str | None):
    query = text("""
        SELECT latitude, longitude, COUNT(*) AS peso
        FROM intel_lead.lead_com_coordenadas
        WHERE (:segmento IS NULL OR segmento = :segmento)
        GROUP BY latitude, longitude
    """)
    result = await db.execute(query, {"segmento": segmento})
    return [tuple(row) for row in result]

# 📊 Resumo estatístico (por filtro)
async def get_resumo(db: AsyncSession, estado: str | None, municipio: str | None, segmento: str | None):
    query = text("""
        SELECT
            COUNT(*) AS total_leads,
            COUNT(cnpj) FILTER (WHERE cnpj IS NOT NULL) AS total_com_cnpj,
            COUNT(*) FILTER (WHERE status = 'enriched') AS total_enriquecidos,
            AVG(pac) AS media_potencia,
            json_object_agg(classe, count(*)) FILTER (WHERE classe IS NOT NULL) AS por_classe
        FROM intel_lead.vw_lead_com_cnae_desc
        WHERE (:estado IS NULL OR estado = :estado)
          AND (:municipio IS NULL OR municipio = :municipio)
          AND (:segmento IS NULL OR segmento = :segmento)
    """)
    result = await db.execute({
        "estado": estado,
        "municipio": municipio,
        "segmento": segmento
    })
    return LeadResumo(**result.mappings().first())
