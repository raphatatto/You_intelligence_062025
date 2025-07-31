import os
import time
import requests
from typing import List
from dotenv import load_dotenv
from datetime import datetime
import psycopg2

load_dotenv()

CNPJA_BASE_URL = "https://api.cnpja.com.br/companies"
CNPJA_TOKEN = os.getenv("CNPJA_API_TOKEN")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": os.getenv("DB_PORT", 5432),
    "sslmode": "require"
}

HEADERS = {
    "Authorization": f"Bearer {CNPJA_TOKEN}"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def log_api(conn, endereco, status_code, tempo_ms, erro=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO enriquecimento_lead.log_api
                (api, tipo, status_code, tempo_resposta_ms, sucesso, erro, endereco)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            "cnpja", "endereco", status_code, tempo_ms,
            status_code == 200, erro, endereco
        ))

def buscar_endereco_google(conn, lead_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT endereco_formatado
            FROM enriquecimento_lead.lead_enriquecido
            WHERE lead_id = %s
            ORDER BY data_enriquecimento DESC
            LIMIT 1
        """, (lead_id,))
        result = cur.fetchone()
        return result[0] if result else None

def buscar_cnpj_por_endereco(endereco: str):
    url = f"{CNPJA_BASE_URL}?q={endereco}"
    start = time.time()
    response = requests.get(url, headers=HEADERS)
    tempo = int((time.time() - start) * 1000)
    return response, tempo

def atualizar_enriquecido(conn, lead_id, empresa):
    now = datetime.utcnow()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE enriquecimento_lead.lead_enriquecido
            SET
                cnpj = %s,
                cnae_principal = %s,
                descricao_cnae = %s,
                situacao_cadastral = %s,
                capital_social = %s,
                data_enriquecimento = %s,
                versao = versao + 1
            WHERE lead_id = %s
        """, (
            empresa.get("cnpj"),
            empresa.get("cnae", {}).get("code"),
            empresa.get("cnae", {}).get("description"),
            empresa.get("status"),
            empresa.get("capital_social"),
            now,
            lead_id
        ))

def enriquecer_leads_cnpj(lead_ids: List[str]):
    conn = get_db()
    try:
        for lead_id in lead_ids:
            endereco = buscar_endereco_google(conn, lead_id)
            if not endereco:
                print(f"⚠️ Lead {lead_id} sem endereço formatado — pulei.")
                continue

            print(f"🔎 Buscando CNPJ para lead {lead_id} ({endereco})")
            res, tempo = buscar_cnpj_por_endereco(endereco)
            status = res.status_code
            log_api(conn, endereco, status, tempo)

            if status != 200:
                print(f"❌ Erro {status} na API")
                continue

            data = res.json()
            empresas = data.get("data") or data  # suporte a ambos formatos

            if not empresas:
                print(f"⚠️ Nenhuma empresa encontrada no endereço")
                continue

            empresa = empresas[0]  # pega a primeira empresa retornada
            atualizar_enriquecido(conn, lead_id, empresa)
            print(f"✅ Lead {lead_id} atualizado com CNPJ {empresa.get('cnpj')}")

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python enrich_cnpj_job.py <lead_id_1> <lead_id_2> ...")
        sys.exit(1)

    lead_ids = sys.argv[1:]
    enriquecer_leads_cnpj(lead_ids)
