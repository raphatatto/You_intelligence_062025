from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.schemas.lead_schema import LeadGeoOut

async def buscar_top_leads_geo(db: AsyncSession, limit: int = 300) -> list[LeadGeoOut]:
    query = text("""
        SELECT 
            lb.uc_id,
            lb.bairro,
            lb.cep,
            lb.descricao AS descr,
            lb.cnae,
            m.uf AS estado,
            lb.tipo_sistema,
            lb.latitude,
            lb.longitude,
            lb.distribuidora_nome AS dist,
            q.media_dic AS dic_med,
            q.media_fic AS fic_med,
            em.ene_01, em.ene_02, em.ene_03, em.ene_04, em.ene_05, em.ene_06,
            em.ene_07, em.ene_08, em.ene_09, em.ene_10, em.ene_11, em.ene_12,
            dm.dem_01, dm.dem_02, dm.dem_03, dm.dem_04, dm.dem_05, dm.dem_06,
            dm.dem_07, dm.dem_08, dm.dem_09, dm.dem_10, dm.dem_11, dm.dem_12,
            qm.dic_01, qm.dic_02, qm.dic_03, qm.dic_04, qm.dic_05, qm.dic_06,
            qm.dic_07, qm.dic_08, qm.dic_09, qm.dic_10, qm.dic_11, qm.dic_12,
            qm.fic_01, qm.fic_02, qm.fic_03, qm.fic_04, qm.fic_05, qm.fic_06,
            qm.fic_07, qm.fic_08, qm.fic_09, qm.fic_10, qm.fic_11, qm.fic_12
        FROM intel_lead.lead_bruto lb
        LEFT JOIN intel_lead.lead_energia_mensal em ON em.lead_bruto_id = lb.id
        LEFT JOIN intel_lead.lead_demanda_mensal dm ON dm.lead_bruto_id = lb.id
        LEFT JOIN intel_lead.lead_qualidade_mensal qm ON qm.lead_bruto_id = lb.id
        LEFT JOIN intel_lead.lead_qualidade q ON q.lead_bruto_id = lb.id
        LEFT JOIN intel_lead.municipio m ON m.id = lb.municipio_id
        WHERE lb.latitude IS NOT NULL 
          AND lb.longitude IS NOT NULL
        LIMIT :limit
    """)
    result = await db.execute(query, {"limit": limit})
    rows = result.mappings().all()
    return [LeadGeoOut(**row) for row in rows]
