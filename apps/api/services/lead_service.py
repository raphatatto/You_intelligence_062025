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

async def list_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = text("""
        SELECT
            l.id,
            i.nome_fantasia AS nome,
            i.cnpj,
            uc.classe,
            uc.grupo_tensao AS subgrupo,
            uc.modalidade,
            i.uf AS estado,
            i.municipio,
            l.distribuidora,
            uc.potencia,
            l.latitude,
            l.longitude,
            uc.segmento,
            l.status,
            uc.cnae,
            lq.dic AS dicMes,
            lq.fic AS ficMes
        FROM plead.lead l
        LEFT JOIN plead.info_leads i ON l.id = i.lead_id
        LEFT JOIN plead.unidade_consumidora uc ON l.id = uc.lead_id
        LEFT JOIN plead.lead_qualidade lq ON uc.id = lq.uc_id
        ORDER BY i.nome_fantasia
        OFFSET :skip
        LIMIT :limit
    """)

    total_query = text("SELECT COUNT(*) FROM plead.lead")

    result = await db.execute(query, {"skip": skip, "limit": limit})
    rows = result.mappings().all()

    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

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

    return total, leads

async def get_lead(db: AsyncSession, lead_id: str) -> LeadDetail | None:
    query = text("""
        SELECT
            l.id,
            i.nome_fantasia AS nome,
            i.cnpj,
            uc.classe,
            uc.grupo_tensao AS subgrupo,
            uc.modalidade,
            i.uf AS estado,
            i.municipio,
            l.distribuidora,
            uc.potencia,
            l.latitude,
            l.longitude,
            uc.segmento,
            l.status,
            uc.cnae,
            uc.data_conexao,
            lq.dic AS dicMes,
            lq.fic AS ficMes
        FROM plead.lead l
        LEFT JOIN plead.info_leads i ON l.id = i.lead_id
        LEFT JOIN plead.unidade_consumidora uc ON l.id = uc.lead_id
        LEFT JOIN plead.lead_qualidade lq ON uc.id = lq.uc_id
        WHERE l.id = :lead_id
    """)

    result = await db.execute(query, {"lead_id": lead_id})
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

async def get_qualidade(db: AsyncSession, lead_id: str) -> LeadQualidade | None:
    query = text("""
        SELECT
            dic,
            fic
        FROM plead.lead_qualidade
        WHERE lead_id = :lead_id
    """)
    result = await db.execute(query, {"lead_id": lead_id})
    row = result.mappings().first()
    if not row:
        return None

    dic_array = parse_array_text(row["dic"])
    fic_array = parse_array_text(row["fic"])

    return LeadQualidade(
        dicMes=dic_array,
        ficMes=fic_array,
        dicMed=round(sum(dic_array) / len(dic_array), 2) if dic_array else None,
        ficMed=round(sum(fic_array) / len(fic_array), 2) if fic_array else None
    )

async def get_map_points(db: AsyncSession, status: str | None, distribuidora: str | None, limit: int = 1000):
    query = text("""
        SELECT
            l.id,
            l.latitude,
            l.longitude,
            uc.classe,
            uc.grupo_tensao AS subgrupo,
            uc.potencia,
            l.distribuidora,
            l.status
        FROM plead.lead l
        LEFT JOIN plead.unidade_consumidora uc ON l.id = uc.lead_id
        WHERE (:status IS NULL OR l.status = :status)
          AND (:distribuidora IS NULL OR l.distribuidora = :distribuidora)
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
            l.latitude,
            l.longitude,
            COUNT(*) as peso
        FROM plead.lead l
        LEFT JOIN plead.unidade_consumidora uc ON l.id = uc.lead_id
        WHERE (:segment IS NULL OR uc.segmento = :segment)
        GROUP BY l.latitude, l.longitude
    """)
    result = await db.execute(query, {"segment": segment})
    return [tuple(row) for row in result]

async def get_resumo(db: AsyncSession, estado: str | None, municipio: str | None, segmento: str | None):
    query = text("""
        SELECT
            COUNT(*) AS total_leads,
            COUNT(i.cnpj) FILTER (WHERE i.cnpj IS NOT NULL) AS total_com_cnpj,
            COUNT(*) FILTER (WHERE l.status = 'enriquecido') AS total_enriquecidos,
            AVG(uc.consumo_medio) AS media_consumo,
            AVG(uc.potencia) AS media_potencia,
            json_object_agg(uc.classe, count(*)) FILTER (WHERE uc.classe IS NOT NULL) AS por_classe
        FROM plead.lead l
        LEFT JOIN plead.info_leads i ON l.id = i.lead_id
        LEFT JOIN plead.unidade_consumidora uc ON l.id = uc.lead_id
        WHERE (:estado IS NULL OR i.uf = :estado)
        AND (:municipio IS NULL OR i.municipio = :municipio)
        AND (:segmento IS NULL OR uc.segmento = :segmento)

    """)
    result = await db.execute(query, {
        "estado": estado,
        "municipio": municipio,
        "segmento": segmento,
    })
    return LeadResumo(**result.mappings().first())
