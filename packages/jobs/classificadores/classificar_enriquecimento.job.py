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

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def calcular_score(lead):
    score = 0
    if lead.get("cnpj"): score += 20
    if lead.get("cnae_principal"): score += 15
    if lead.get("descricao_atividade"): score += 10
    if lead.get("nome_fantasia") or lead.get("razao_social"): score += 10
    if lead.get("situacao_cadastral") and "ativa" in lead["situacao_cadastral"].lower(): score += 10
    if lead.get("endereco_formatado"): score += 5
    if lead.get("fonte") == "google": score += 5
    if lead.get("capital_social") and float(lead["capital_social"]) > 10000: score += 5
    return min(score, 100)

def status_por_score(score):
    if score >= 90: return "full"
    elif score >= 70: return "good"
    elif score >= 50: return "partial"
    elif score > 0: return "falho"
    else: return "raw"

def classificar_leads():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lead_id, cnpj, cnae_principal, descricao_atividade, nome_fantasia,
                       razao_social, situacao_cadastral, endereco_formatado, fonte, capital_social
                FROM enriquecimento_lead.lead_enriquecido
            """)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

        atualizacoes = []
        for row in rows:
            lead = dict(zip(cols, row))
            score = calcular_score(lead)
            status = status_por_score(score)
            atualizacoes.append((score, status, lead["lead_id"]))

        with conn.cursor() as cur:
            for score, status, lead_id in atualizacoes:
                cur.execute("""
                    UPDATE enriquecimento_lead.lead_enriquecido
                    SET enrich_score = %s,
                        status_enriquecimento = %s
                    WHERE lead_id = %s
                """, (score, status, lead_id))

        conn.commit()
        print(f"✅ Classificação finalizada para {len(atualizacoes)} leads.")
    finally:
        conn.close()

if __name__ == "__main__":
    classificar_leads()
