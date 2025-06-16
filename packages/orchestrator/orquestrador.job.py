import json
import shutil
import requests
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime
from importer_ucmt import importar_ucmt
from importer_ucat import importar_ucat
from importer_ucbt import importar_ucbt
from psycopg2 import connect

# ─── CONFIG ────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "dbname": "youon",
    "user": "postgres",
    "password": "your_password_here"
}

DOWNLOAD_FOLDER = Path("data/downloads")
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# ─── FUNÇÕES DE STATUS ────────────────────────────────────────
def ja_importado(distribuidora, ano, camada):
    try:
        conn = connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM import_status
            WHERE distribuidora = %s AND ano = %s AND camada = %s AND status = 'success'
        """, (distribuidora, ano, camada))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result)
    except Exception as e:
        print(f"❌ Erro ao verificar status no banco: {e}")
        return False

def salvar_status(distribuidora, ano, camada, status):
    try:
        conn = connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (distribuidora, ano, camada)
            DO UPDATE SET status = EXCLUDED.status, data_execucao = EXCLUDED.data_execucao
        """, (distribuidora, ano, camada, status, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        print(f"🧾 Status salvo: {distribuidora} {ano} {camada} → {status}")
    except Exception as e:
        print(f"❌ Erro ao salvar status no banco: {e}")

# ─── DOWNLOAD ─────────────────────────────────────────────────
def gerar_link_zip(about_url: str) -> str:
    parts = about_url.strip("/").split("/")
    arcgis_id = parts[-2] if parts[-1] == "about" else parts[-1]
    return f"https://www.arcgis.com/sharing/rest/content/items/{arcgis_id}/data"

def baixar_zip_if_needed(distribuidora, ano, about_url):
    zip_path = None
    for file in DOWNLOAD_FOLDER.glob("*.zip"):
        if distribuidora in file.name.lower() and str(ano) in file.name:
            zip_path = file
            break

    if zip_path:
        print(f"🟡 ZIP já existe localmente: {zip_path.name}")
        return zip_path

    print("📥 Baixando ZIP...")
    zip_url = gerar_link_zip(about_url)
    response = requests.get(zip_url, stream=True, verify=False)

    nome_arquivo = response.headers.get("Content-Disposition", "arquivo_desconhecido.zip")
    if "filename=" in nome_arquivo:
        nome_arquivo = nome_arquivo.split("filename=")[-1].replace('"', '').strip()
    else:
        nome_arquivo = f"{distribuidora}_{ano}.zip"

    zip_path = DOWNLOAD_FOLDER / nome_arquivo
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ ZIP salvo: {zip_path.name}")
    return zip_path

# ─── EXECUÇÃO DO ORQUESTRADOR ────────────────────────────────
def main():
    with open("aneel_datasets.json", "r", encoding="utf-8") as f:
        datasets = json.load(f)

    for item in datasets:
        distribuidora = item["distribuidora"].lower()
        ano = int(item["ano"])
        about_url = item["url_arcgis"]

        try:
            zip_path = baixar_zip_if_needed(distribuidora, ano, about_url)
            extract_folder = DOWNLOAD_FOLDER / zip_path.stem.replace(".gdb", "")
            if not any(extract_folder.glob("*.gdb")):
                print("📂 Extraindo GDB...")
                with ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                print(f"✅ Extraído para: {extract_folder}")

            camada_jobs = {
                "UCMT_tab": importar_ucmt,
                "UCBT_tab": importar_ucbt,
                "UCAT_tab": importar_ucat,
            }

            for camada, job_func in camada_jobs.items():
                if ja_importado(distribuidora, ano, camada):
                    print(f"✅ {camada} já importada para {distribuidora} {ano}, pulando...")
                    continue

                try:
                    job_func(extract_folder, distribuidora, ano)
                    salvar_status(distribuidora, ano, camada, "success")
                except Exception as err:
                    print(f"❌ Erro ao importar {camada}: {err}")
                    salvar_status(distribuidora, ano, camada, "error")

        except Exception as e:
            print(f"❌ Erro geral para {distribuidora} {ano}: {e}")

if __name__ == "__main__":
    main()
