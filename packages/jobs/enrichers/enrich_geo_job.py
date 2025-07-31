import os
import time
import requests
from typing import List
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
RAIO_METROS = 100

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

def log_api(conn, lat, lon, status, tempo, erro=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO enriquecimento_lead.log_api
                (api, tipo, latitude, longitude, status_code, tempo_resposta_ms, sucesso, erro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, ("google", "places", lat, lon, status, tempo, status == "200", erro))

def checar_cache(conn, lat, lon, raio):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT cnpjs FROM enriquecimento_lead.cache_geo_cnpj
            WHERE latitude = %s AND longitude = %s AND raio = %s
        """, (lat, lon, raio))
        result = cur.fetchone()
        return result[0] if result else None

def salvar_cache(conn, lat, lon, raio, place_ids):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO enriquecimento_lead.cache_geo_cnpj
                (latitude, longitude, raio, cnpjs, fonte)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (lat, lon, raio, place_ids, "google"))

def buscar_places(lat, lon, raio):
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={lat},{lon}&radius={raio}&key={API_KEY}"
    )
    start = time.time()
    res = requests.get(url)
    elapsed = int((time.time() - start) * 1000)
    return res, elapsed

def buscar_place_details(place_id):
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,types"
        f"&key={API_KEY}"
    )
    return requests.get(url).json()

def salvar_resultado(conn, lead_id, dados, raio):
    now = datetime.utcnow()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO enriquecimento_lead.lead_enriquecido (
                lead_id, razao_social, nome_fantasia, descricao_atividade,
                endereco_formatado, fonte, raio_utilizado, data_enriquecimento, versao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            lead_id,
            dados.get("name"),
            dados.get("name"),
            ", ".join(dados.get("types", []))[:200],
            dados.get("formatted_address"),
            "google",
            raio,
            now,
            1
        ))

def enriquecer_leads_google(leads: List[str]):
    conn = get_db()
    try:
        for lead_id in leads:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT latitude, longitude
                    FROM intel_lead.lead_bruto
                    WHERE uc_id = %s
                """, (lead_id,))
                row = cur.fetchone()
                if not row:
                    print(f"❌ Lead {lead_id} não encontrado.")
                    continue
                lat, lon = row

            if checar_cache(conn, lat, lon, RAIO_METROS):
                print(f"⚠️ Lead {lead_id} já em cache, ignorando...")
                continue

            print(f"🔎 Enriquecendo lead {lead_id} via Google...")
            res, tempo = buscar_places(lat, lon, RAIO_METROS)
            status = str(res.status_code)
            log_api(conn, lat, lon, status, tempo)

            if status != "200":
                print(f"❌ Erro {status} na API")
                continue

            data = res.json()
            places = data.get("results", [])
            if not places:
                print(f"⚠️ Nenhum lugar encontrado no raio para lead {lead_id}")
                continue

            melhor = places[0]
            detalhes = buscar_place_details(melhor["place_id"])
            result = detalhes.get("result", {})
            if "name" not in result:
                continue

            salvar_resultado(conn, lead_id, result, RAIO_METROS)
            salvar_cache(conn, lat, lon, RAIO_METROS, [melhor["place_id"]])
            print(f"✅ Enriquecido com {result['name']}")

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python enrich_geo_job.py <lead_id_1> <lead_id_2> ...")
        sys.exit(1)

    lead_ids = sys.argv[1:]
    enriquecer_leads_google(lead_ids)
