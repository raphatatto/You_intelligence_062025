from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.lead_schema import (
    LeadDetalhado,
    LeadQualidade,
    LeadResumo,
    LeadMapOut,
    LeadList,
    LeadOut
)
import json

# 🔢 Parser auxiliar para arrays de texto
def parse_array_text(texto: str | None) -> list[float] | None:
    if not texto:
        return None
    try:
        return [float(x) for x in texto.strip("{} ").split(",") if x]
    except Exception:
        return None


# 🔍 Listagem com filtros e paginação
async def buscar_leads(
    db: AsyncSession,
    estado: str | None,
    tipo: str | None,
    distribuidora: str | None,
    segmento: str | None,
    ordem: str,
    busca: str | None,
    skip: int,
    limit: int,
) -> LeadList:
    filtros = []
    params = {"skip": skip, "limit": limit}

    if estado:
        filtros.append("estado = :estado")
        params["estado"] = estado
    if tipo:
        filtros.append("classe = :tipo")
        params["tipo"] = tipo
    if distribuidora:
        filtros.append("distribuidora_nome = :distribuidora")
        params["distribuidora"] = distribuidora
    if segmento:
        filtros.append("segmento_desc = :segmento")
        params["segmento"] = segmento
    if busca:
        filtros.append("(bairro ILIKE :busca OR descricao ILIKE :busca)")
        params["busca"] = f"%{busca}%"

    where_clause = "WHERE " + " AND ".join(filtros) if filtros else ""

    ordenacoes = {
        "padrao": "distribuidora_nome",
        "dic_asc": "media_dic ASC",
        "dic_desc": "media_dic DESC",
        "fic_asc": "media_fic ASC",
        "fic_desc": "media_fic DESC",
        "potencia_desc": "pac DESC",
        "potencia_asc": "pac ASC"
    }
    order_clause = f"ORDER BY {ordenacoes.get(ordem, 'distribuidora_nome')}"

    count_query = text(f"""
        SELECT COUNT(*) FROM intel_lead.vw_lead_completo_detalhado
        {where_clause}
    """)
    total = (await db.execute(count_query, params)).scalar_one()

    query = text(f"""
        SELECT * FROM intel_lead.vw_lead_completo_detalhado
        {where_clause}
        {order_clause}
        OFFSET :skip LIMIT :limit
    """)
    result = await db.execute(query, params)
    rows = result.mappings().all()

    return LeadList(
        total=total,
        items=[LeadOut(**row) for row in rows]
    )


# 📋 Detalhamento individual
async def get_lead(db: AsyncSession, uc_id: str) -> LeadDetalhado | None:
    query = text("""
        SELECT * FROM intel_lead.vw_lead_com_cnae_desc
        WHERE uc_id = :uc_id
    """)
    result = await db.execute(query, {"uc_id": uc_id})
    row = result.mappings().first()
    return LeadDetalhado(**row) if row else None


# 📉 Qualidade DIC/FIC
async def get_qualidade(db: AsyncSession, uc_id: str) -> LeadQualidade | None:
    query = text("""
        SELECT qm.dic, qm.fic
        FROM intel_lead.lead_qualidade_mensal qm
        JOIN intel_lead.lead_bruto lb ON lb.id = qm.lead_bruto_id
        WHERE lb.uc_id = :uc_id
        LIMIT 1
    """)
    result = await db.execute({"uc_id": uc_id})
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


# 🗺️ Pontos para mapa
async def get_map_points(
    db: AsyncSession,
    status: str | None,
    distribuidora: str | None,
    limit: int,
) -> list[LeadMapOut]:
    query = text("""
        SELECT uc_id, latitude, longitude, classe, grupo_tensao, pac AS potencia, distribuidora_nome AS distribuidora, status
        FROM intel_lead.lead_com_coordenadas
        WHERE (:status IS NULL OR status = :status)
          AND (:distribuidora IS NULL OR distribuidora_nome = :distribuidora)
        LIMIT :limit
    """)
    result = await db.execute({
        "status": status,
        "distribuidora": distribuidora,
        "limit": limit
    })
    rows = result.mappings().all()
    return [LeadMapOut(**row) for row in rows]


# 🔥 Heatmap
async def heatmap_points(db: AsyncSession, segmento: str | None) -> list[tuple]:
    query = text("""
        SELECT latitude, longitude, COUNT(*) AS peso
        FROM intel_lead.lead_com_coordenadas
        WHERE (:segmento IS NULL OR segmento_desc = :segmento)
        GROUP BY latitude, longitude
    """)
    result = await db.execute({"segmento": segmento})
    return [tuple(row) for row in result]


# 📊 Resumo
async def get_resumo(
    db: AsyncSession,
    estado: str | None,
    municipio: str | None,
    segmento: str | None
) -> LeadResumo:
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
          AND (:segmento IS NULL OR segmento_desc = :segmento)
    """)
    result = await db.execute({
        "estado": estado,
        "municipio": municipio,
        "segmento": segmento
    })
    row = result.mappings().first()

    return LeadResumo(
        total_leads=row["total_leads"],
        total_com_cnpj=row["total_com_cnpj"],
        total_enriquecidos=row["total_enriquecidos"],
        media_potencia=row["media_potencia"],
        por_classe=json.loads(row["por_classe"]) if row["por_classe"] else {}
    )
