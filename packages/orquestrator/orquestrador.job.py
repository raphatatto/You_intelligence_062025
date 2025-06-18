# packages/orquestrator/orquestrador.job.py

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import json
import shutil
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from datetime import datetime
from packages.jobs.importers.importer_ucmt import importar_ucmt
from packages.jobs.importers.importer_ucat import importar_ucat
from packages.jobs.importers.importer_ucbt import importar_ucbt
from packages.database.connection import get_db_cursor

DOWNLOAD_FOLDER = Path("data/downloads")
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# ─── FUNÇÕES DE STATUS ────────────────────────────────────────

def ja_importado(distribuidora, ano, camada) -> bool:
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 1 FROM import_status
                WHERE distribuidora = %s AND ano = %s AND camada = %s AND status = 'success'
            """, (distribuidora, ano, camada))
            return bool(cur.fetchone())
    except Exception as e:
        print(f"❌ Erro ao verificar status no banco: {e}")
        return False


def salvar_status(distribuidora, ano, camada, status):
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (distribuidora, ano, camada)
                DO UPDATE SET status = EXCLUDED.status, data_execucao = EXCLUDED.data_execucao
            """, (distribuidora, ano, camada, status, datetime.now()))
        print(f"🧾 Status salvo: {distribuidora} {ano} {camada} → {status}")
    except Exception as e:
        print(f"❌ Erro ao salvar status no banco: {e}")


# ─── RESOLVER LINK VERDADEIRO VIA SCRAPING ───────────────────

def gerar_link_zip(about_url: str) -> str:
    """
    Faz scraping da página HTML da ANEEL (accessURL) para extrair o link real de download do .zip.
    """
    try:
        response = requests.get(about_url, verify=False, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/sharing/rest/content/items/" in href and href.endswith("/data"):
                return href

        raise Exception("❌ Link de download não encontrado na página HTML.")

    except Exception as e:
        raise RuntimeError(f"Erro ao gerar link ZIP via scraping: {e}")


# ─── DOWNLOAD ZIP ─────────────────────────────────────────────

def baixar_zip_if_needed(distribuidora, ano, about_url) -> Path:
    for file in DOWNLOAD_FOLDER.glob("*.zip"):
        if distribuidora in file.name.lower() and str(ano) in file.name:
            print(f"🟡 ZIP já existe localmente: {file.name}")
            return file

    print("📥 Baixando ZIP...")
    zip_url = gerar_link_zip(about_url)
    response = requests.get(zip_url, stream=True, verify=False)

    nome_arquivo = response.headers.get("Content-Disposition", f"{distribuidora}_{ano}.zip")
    if "filename=" in nome_arquivo:
        nome_arquivo = nome_arquivo.split("filename=")[-1].replace('"', '').strip()

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
        try:
            # Extrai distribuidora e ano a partir do título
            title = item.get("title", "")
            parts = title.split(" - ")
            if len(parts) != 2:
                print(f"⚠️  Título inválido: {title}")
                continue

            distribuidora = parts[0].strip().lower()
            ano = int(parts[1].split("-")[0])
            about_url = item["resources"][0]["url"].strip()

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
            print(f"❌ Erro geral para item {item.get('title', '')}: {e}")


if __name__ == "__main__":
    main()
