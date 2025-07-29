# packages/jobs/enrichers/enrich_geo_job.py

from packages.database.connection import get_db_connection
from tqdm import tqdm
import pandas as pd

def enrich_geo_info():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Busca os leads brutos com status 'raw' e sem lat/long
    cursor.execute("""
        SELECT uc_id, municipio_id, bairro, cep
        FROM intel_lead.lead_bruto
        WHERE status = 'raw' AND (latitude IS NULL OR longitude IS NULL)
        LIMIT 100
    """)
    rows = cursor.fetchall()

    if not rows:
        tqdm.write("✅ Nenhum lead para geocodificar.")
        return

    for uc_id, municipio_id, bairro, cep in rows:
        # Aqui viria a chamada da API real (Google Maps, IBGE, etc.)
        latitude = -23.5  # ⚠️ mock
        longitude = -46.6

        cursor.execute("""
            UPDATE intel_lead.lead_bruto
            SET latitude = %s,
                longitude = %s
            WHERE uc_id = %s
        """, (latitude, longitude, uc_id))

    conn.commit()
    cursor.close()
    conn.close()
    tqdm.write(f"🌍 Geoinformação enriquecida para {len(rows)} leads.")

if __name__ == "__main__":
    enrich_geo_info()
