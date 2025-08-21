# packages/detectors/diagnoser.py

from sqlalchemy import text


def diagnosticar_uc(uc_id: str, db) -> dict:
    """
    Consulta dados agregados da UC e gera um diagnóstico com sugestões.
    """
    query = text("""
        SELECT 
            uc_id, 
            media_energia_total, 
            media_dic, 
            media_fic, 
            pac, 
            classe, 
            modalidade_tarifaria
        FROM intel_lead.vw_lead_completo_detalhado
        WHERE uc_id = :uc_id
    """)

    res = db.execute(query, {"uc_id": uc_id})
    row = res.fetchone()
    if not row:
        return {}

    data = dict(row)

    # Diagnóstico simples baseado em regras
    insights = []

    if data["media_dic"] and data["media_dic"] > 10:
        insights.append("Alta frequência de quedas (DIC > 10)")
    if data["media_fic"] and data["media_fic"] > 15:
        insights.append("Alta duração das quedas (FIC > 15)")
    if data["media_energia_total"] and data["media_energia_total"] > 5000:
        insights.append("Consumo alto: perfil para GD ou ACL")
    if data["pac"] and data["pac"] > 10000:
        insights.append("PAC elevado: verificar dimensionamento")
    if data["classe"] == "comercial" and data["modalidade_tarifaria"] == "convencional":
        insights.append("Potencial para migração para branco ou ACL")

    return {
        "uc_id": uc_id,
        "media_energia_total": data["media_energia_total"],
        "media_dic": data["media_dic"],
        "media_fic": data["media_fic"],
        "pac": data["pac"],
        "classe": data["classe"],
        "modalidade_tarifaria": data["modalidade_tarifaria"],
        "insights": insights
    }
