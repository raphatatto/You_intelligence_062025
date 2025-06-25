from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.lead import LeadOut, LeadQualidade

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
            lq.dic AS "dicMed",
            lq.fic AS "ficMed",
            ARRAY[
                lq.dic_jan, lq.dic_fev, lq.dic_mar, lq.dic_abr, lq.dic_mai, lq.dic_jun,
                lq.dic_jul, lq.dic_ago, lq.dic_set, lq.dic_out, lq.dic_nov, lq.dic_dez
            ] AS "dicMes",
            ARRAY[
                lq.fic_jan, lq.fic_fev, lq.fic_mar, lq.fic_abr, lq.fic_mai, lq.fic_jun,
                lq.fic_jul, lq.fic_ago, lq.fic_set, lq.fic_out, lq.fic_nov, lq.fic_dez
            ] AS "ficMes"
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

    leads = [LeadOut(**row) for row in rows]
    return total, leads


async def get_qualidade(db: AsyncSession, lead_id: str) -> LeadQualidade | None:
    query = text("""
        SELECT
            dic AS "dicMed",
            fic AS "ficMed",
            ARRAY[
                dic_jan, dic_fev, dic_mar, dic_abr, dic_mai, dic_jun,
                dic_jul, dic_ago, dic_set, dic_out, dic_nov, dic_dez
            ] AS "dicMes",
            ARRAY[
                fic_jan, fic_fev, fic_mar, fic_abr, fic_mai, fic_jun,
                fic_jul, fic_ago, fic_set, fic_out, fic_nov, fic_dez
            ] AS "ficMes"
        FROM lead_qualidade
        WHERE lead_id = :lead_id
    """)
    result = await db.execute(query, {"lead_id": lead_id})
    row = result.first()
    if not row:
        return None
    return LeadQualidade(**row._mapping)
