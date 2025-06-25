from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.lead import LeadOut
from apps.api.schemas.lead import LeadQualidade

async def list_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = text("""
        SELECT
            lb.id,
            lb.nome_uc AS nome,
            lb.cnpj,
            lb.classe,
            lb.subgrupo,
            lb.modalidade,
            lb.estado,
            lb.municipio_ibge AS municipio,
            lb.distribuidora,
            le.potencia,
            (lb.coordenadas->>'lat')::float AS latitude,
            (lb.coordenadas->>'lng')::float AS longitude,
            lb.segmento,
            lb.status,
            lb.cnae,
            lq.dic AS "dicMed",
            lq.fic AS "ficMed"
        FROM lead_bruto lb
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
