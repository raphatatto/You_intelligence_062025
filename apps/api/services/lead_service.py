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
        return [float(x) for x in text.strip("{}").split(",")]
    except Exception:
        return None

async def list_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = text("""
        SELECT
            lb.id,
            lb.nome_uc AS nome,
            lb.cnpj,
            lb.classe,
            lb.subgrupo,
            lb.modalidade,
            gi.estado,
            gi.cidade AS municipio,
            lb.distribuidora,
            le.potencia,
            (lb.coordenadas->>'lat')::float AS latitude,
            (lb.coordenadas->>'lng')::float AS longitude,
            lb.segmento,
            lb.status,
            lb.cnae,
            lq.dic AS dicBruta,
            lq.fic AS ficBruta
        FROM lead_bruto lb
        LEFT JOIN geo_info_lead gi ON lb.id = gi.lead_id
        LEFT JOIN lead_energia le ON lb.id = le.lead_id
        LEFT JOIN lead_qualidade lq ON lb.id = lq.lead_id
        ORDER BY lb.nome_uc
        OFFSET :skip
        LIMIT :limit
    """)

    total_query = text("SELECT COUNT(*) FROM lead_bruto")

    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.mappings().all()

    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    leads = []
    for row in rows:
        data = dict(row)
        data["dicMes"] = parse_array_text(data.get("dicBruta"))
        data["ficMes"] = parse_array_text(data.get("ficBruta"))
        data.pop("dicBruta", None)
        data.pop("ficBruta", None)
        leads.append(LeadOut(**data))

    return total, leads

async def get_lead(db: AsyncSession, lead_id: str) -> LeadDetail | None:
    query = text("""
        SELECT
            lb.id,
            lb.nome_uc AS nome,
            lb.cnpj,
            lb.classe,
            lb.subgrupo,
            lb.modalidade,
            gi.estado,
            gi.cidade AS municipio,
            lb.distribuidora,
            le.potencia,
            (lb.coordenadas->>'lat')::float AS latitude,
            (lb.coordenadas->>'lng')::float AS longitude,
            lb.segmento,
            lb.status,
            lb.cnae,
            lb.data_conexao,
            lq.dic AS dicBruta,
            lq.fic AS ficBruta
        FROM lead_bruto lb
        LEFT JOIN geo_info_lead gi ON lb.id = gi.lead_id
        LEFT JOIN lead_energia le ON lb.id = le.lead_id
        LEFT JOIN lead_qualidade lq ON lb.id = lq.lead_id
        WHERE lb.id = :lead_id
    """)

    result = await db.execute(query, {"lead_id": lead_id})
    row = result.mappings().first()
    if not row:
        return None

    data = dict(row)
    data["dicMes"] = parse_array_text(data.get("dicBruta"))
    data["ficMes"] = parse_array_text(data.get("ficBruta"))
    data["dicMed"] = round(sum(data["dicMes"]) / len(data["dicMes"]), 2) if data["dicMes"] else None
    data["ficMed"] = round(sum(data["ficMes"]) / len(data["ficMes"]), 2) if data["ficMes"] else None
    data.pop("dicBruta", None)
    data.pop("ficBruta", None)

    return LeadDetail(**data)

async def get_qualidade(db: AsyncSession, lead_id: str) -> LeadQualidade | None:
    query = text("""
        SELECT
            dic AS dicMed,
            fic AS ficMed
        FROM lead_qualidade
        WHERE lead_id = :lead_id
    """)
    result = await db.execute(query, {"lead_id": lead_id})
    row = result.first()
    if not row:
        return None

    data = dict(row._mapping)
    data["dicMes"] = parse_array_text(data.get("dicMed"))
    data["ficMes"] = parse_array_text(data.get("ficMed"))
    return LeadQualidade(**data)

async def get_map_points(db: AsyncSession, status: str | None, distribuidora: str | None, limit: int = 1000):
    query = text("""
        SELECT
            lb.id,
            (lb.coordenadas->>'lat')::float AS latitude,
            (lb.coordenadas->>'lng')::float AS longitude,
            lb.classe,
            lb.subgrupo,
            le.potencia,
            lb.distribuidora,
            lb.status
        FROM lead_bruto lb
        LEFT JOIN lead_energia le ON lb.id = le.lead_id
        WHERE (:status IS NULL OR lb.status = :status)
          AND (:distribuidora IS NULL OR lb.distribuidora = :distribuidora)
        LIMIT :limit
    """)
    result = await db.execute(query, {
        "status": status,
        "distribuidora": distribuidora,
        "limit": limit
    })
    return [LeadMapOut(**row._mapping) for row in result]

async def heatmap_points(db: AsyncSession, segment: str | None):
    query = text("""
        SELECT
            (lb.coordenadas->>'lat')::float AS latitude,
            (lb.coordenadas->>'lng')::float AS longitude,
            COUNT(*) as peso
        FROM lead_bruto lb
        WHERE (:segment IS NULL OR lb.segmento = :segment)
        GROUP BY latitude, longitude
    """)
    result = await db.execute(query, {"segment": segment})
    return [tuple(row) for row in result]

async def get_resumo(db: AsyncSession, estado: str | None, municipio: str | None, segmento: str | None):
    query = text("""
        SELECT
            COUNT(*) AS total_leads,
            COUNT(cnpj) FILTER (WHERE cnpj IS NOT NULL) AS total_com_cnpj,
            COUNT(*) FILTER (WHERE status = 'enriquecido') AS total_enriquecidos,
            AVG(le.consumo_medio) AS media_consumo,
            AVG(le.potencia) AS media_potencia,
            json_object_agg(classe, count(*)) FILTER (WHERE classe IS NOT NULL) AS por_classe
        FROM lead_bruto lb
        LEFT JOIN geo_info_lead gi ON lb.id = gi.lead_id
        LEFT JOIN lead_energia le ON lb.id = le.lead_id
        WHERE (:estado IS NULL OR gi.estado = :estado)
          AND (:municipio IS NULL OR gi.cidade = :municipio)
          AND (:segmento IS NULL OR lb.segmento = :segmento)
    """)
    result = await db.execute(query, {
        "estado": estado,
        "municipio": municipio,
        "segmento": segmento,
    })
    return LeadResumo(**result.mappings().first())
