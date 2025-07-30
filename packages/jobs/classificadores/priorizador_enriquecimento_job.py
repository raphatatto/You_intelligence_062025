import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": os.getenv("DB_PORT", 5432),
    "sslmode": "require"
}

ESTADOS_PRIORITARIOS = {"SP", "RJ", "MG", "PR", "RS"}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def classificar_lead(lead):
    uc_id, tipo_uc, estado, latitude, longitude, consumo, dic, fic = lead

    if not latitude or not longitude or latitude == 0 or longitude == 0:
        return "desativado"

    if tipo_uc == "UCAT":
        return "standby"

    if estado not in ESTADOS_PRIORITARIOS:
        return "standby"

    if consumo and consumo > 5000 and (dic is None or dic < 10) and (fic is None or fic < 10):
        return "prioritario"

    return "standby"

def priorizar_leads():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lb.uc_id, lb.tipo_uc, m.estado, lb.latitude, lb.longitude,
                       e.media_energia_total, q.dic_ultimo_ano, q.fic_ultimo_ano
                FROM intel_lead.lead_bruto lb
                LEFT JOIN intel_lead.lead_energia e ON lb.uc_id = e.uc_id
                LEFT JOIN intel_lead.lead_qualidade q ON lb.uc_id = q.uc_id
                LEFT JOIN public.municipios m ON lb.municipio_id = m.id
                WHERE lb.status = 'raw'
            """)
            leads = cur.fetchall()
            print(f"🔍 Avaliando {len(leads)} leads com status 'raw'")

        atualizacoes = []
        for lead in leads:
            status = classificar_lead(lead)
            atualizacoes.append((status, lead[0]))

        with conn.cursor() as cur:
            for status, uc_id in atualizacoes:
                cur.execute("""
                    UPDATE intel_lead.lead_bruto
                    SET status = %s
                    WHERE uc_id = %s
                """, (status, uc_id))

        conn.commit()
        print(f"✅ Priorizações aplicadas: {len(atualizacoes)} leads reclassificados")
    finally:
        conn.close()

if __name__ == "__main__":
    priorizar_leads()
