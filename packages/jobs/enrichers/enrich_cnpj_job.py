# packages/jobs/enrichers/enrich_cnpj_job.py

from packages.database.connection import get_db_connection
from tqdm import tqdm

def enrich_cnpj():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT uc_id, latitude, longitude
        FROM intel_lead.lead_bruto
        WHERE status = 'raw' AND latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 100
    """)
    rows = cursor.fetchall()

    if not rows:
        tqdm.write("✅ Nenhum lead com coordenadas para enriquecer CNPJ.")
        return

    for uc_id, lat, lng in rows:
        # Chamada à API do CNPJá, ReceitaWS, etc. (aqui mockado)
        cnpj = "12.345.678/0001-90"
        nome = "EMPRESA TESTE LTDA"
        cnae = "4711-3/02"

        cursor.execute("""
            UPDATE intel_lead.lead_bruto
            SET cnpj = %s,
                nome_empresarial = %s,
                cnae = %s,
                status = 'enriched'
            WHERE uc_id = %s
        """, (cnpj, nome, cnae, uc_id))

    conn.commit()
    cursor.close()
    conn.close()
    tqdm.write(f"🏢 CNPJ enriquecido para {len(rows)} leads.")

if __name__ == "__main__":
    enrich_cnpj()
