import zipfile
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import requests
import time
import sys

from psycopg2.extras import RealDictCursor
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from packages.database.connection import get_db_connection

# Caminhos
DOWNLOAD_DIR = Path("data/downloads")
TMP_DIR = Path("data/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Camadas que serão extraídas
CAMADAS_VALIDAS = {"UCAT", "UCMT", "UCBT", "PONNOT"}

def registrar_log(distribuidora, ano, status, erro=None, tempo_download=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM intel_lead.download_log
                WHERE distribuidora = %s AND ano = %s
            """, (distribuidora, ano))
            row = cur.fetchone()

            if row:
                cur.execute("""
                    UPDATE intel_lead.download_log
                    SET status = %s,
                        erro = %s,
                        tempo_download = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (status, erro, tempo_download, row[0]))
                return row[0]
            else:
                cur.execute("""
                    INSERT INTO intel_lead.download_log (
                        distribuidora, ano, status, erro, tempo_download
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (distribuidora, ano, status, erro, tempo_download))
                return cur.fetchone()[0]

def obter_url_gdb(distribuidora: str, ano: int) -> tuple[str, str]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT title, url
                FROM intel_lead.dataset_url_catalog
                WHERE lower(title) LIKE %s
                  AND title ILIKE %s
                  AND tipo = 'File Geodatabase'
                LIMIT 1
            """, (f"%{distribuidora.lower()}%", f"%{ano}%"))
            row = cursor.fetchone()
            if not row:
                raise Exception(f"❌ Nenhum GDB encontrado no banco para {distribuidora}_{ano}")
            return row["title"], row["url"]

def baixar_arquivo(url: str, destino: Path):
    print(f"⬇️  Baixando: {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(destino, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"✅ Download salvo em: {destino}")

def extrair_gdb(zip_path: Path, destino_final: Path):
    print(f"📦 Extraindo {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(TMP_DIR)

    count = 0
    for item in TMP_DIR.iterdir():
        if item.is_dir() and any(camada in item.name.upper() for camada in CAMADAS_VALIDAS):
            final_path = destino_final / item.name
            shutil.move(str(item), final_path)
            print(f"✅ .gdb extraído: {final_path}")
            count += 1

    zip_path.unlink()
    shutil.rmtree(TMP_DIR, ignore_errors=True)

    if count == 0:
        print("⚠️ Nenhuma camada relevante encontrada.")

def baixar_gdb(distribuidora: str, ano: int):
    log_id = registrar_log(distribuidora, ano, "downloading")
    try:
        start = time.time()
        title, url = obter_url_gdb(distribuidora, ano)
        nome_base = title.replace(" ", "_").replace("-", "_")
        zip_path = TMP_DIR / f"{nome_base}.zip"

        # Evita baixar de novo
        if any(Path(DOWNLOAD_DIR / d).exists() for d in os.listdir(DOWNLOAD_DIR) if f"{distribuidora}" in d and str(ano) in d):
            print("⚠️ Arquivo já existente. Pulando download.")
            registrar_log(distribuidora, ano, "done", tempo_download=0)
            return

        baixar_arquivo(url, zip_path)
        registrar_log(distribuidora, ano, "extracting")

        extrair_gdb(zip_path, DOWNLOAD_DIR)
        tempo = time.time() - start
        registrar_log(distribuidora, ano, "done", tempo_download=tempo)

    except Exception as e:
        registrar_log(distribuidora, ano, "error", erro=str(e))
        raise

# Modo terminal ou CLI
if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribuidora", required=False)
    parser.add_argument("--ano", required=False, type=int)
    args = parser.parse_args()

    if args.distribuidora and args.ano:
        baixar_gdb(args.distribuidora, args.ano)
    else:
        print("🔧 Modo interativo")
        dist = input("Distribuidora: ")
        ano = int(input("Ano: "))
        baixar_gdb(dist, ano)
