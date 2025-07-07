import os
import json
import zipfile
import shutil
import requests
from tqdm import tqdm
from pathlib import Path
from subprocess import run

from packages.jobs.utils.rastreio import get_status


DATASETS_JSON = Path("data/datasets.json")
DOWNLOADS_DIR = Path("data/downloads/")
CAMADAS = ["UCAT", "UCMT", "UCBT", "PONNOT"]
IMPORTERS = {
    "UCAT": "packages/jobs/importers/importer_ucat.job.py",
    "UCMT": "packages/jobs/importers/importer_ucmt.job.py",
    "UCBT": "packages/jobs/importers/importer_ucbt.job.py",
    "PONNOT": "packages/jobs/importers/importer_ponnot.job.py",
}


def baixar_zip(url: str, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        tqdm.write(f"📦 Já existe: {destino.name}")
        return

    tqdm.write(f"⬇️ Baixando: {url}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(destino, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def extrair_zip(arquivo_zip: Path, destino: Path):
    if destino.exists():
        tqdm.write(f"📂 Já extraído: {destino}")
        return

    tqdm.write(f"🗜️ Extraindo: {arquivo_zip.name}")
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(destino)


def rodar_importer(script_path: str, gdb_path: Path, camada: str, distribuidora: str, ano: int, prefixo: str):
    status = get_status(prefixo, ano, camada)
    if status == "success":
        tqdm.write(f"✅ Já importado: {camada} {prefixo} {ano}")
        return

    tqdm.write(f"⚙️  Importando {camada} para {prefixo} {ano}")
    run([
        "python", script_path,
        "--gdb", str(gdb_path),
        "--ano", str(ano),
        "--distribuidora", distribuidora,
        "--prefixo", prefixo
    ], check=False)


def main():
    tqdm.write("📁 Iniciando orquestrador de ingestão batch...")
    with open(DATASETS_JSON, "r", encoding="utf-8") as f:
        datasets = json.load(f)

    for ds in tqdm(datasets, desc="Distribuidoras"):
        prefixo = ds["id"]
        ano = ds["ano"]
        distribuidora = ds["distribuidora"]
        url = ds["download"]

        zip_path = DOWNLOADS_DIR / f"{prefixo}_{ano}.zip"
        extract_dir = DOWNLOADS_DIR / f"{prefixo}_{ano}"
        gdb_dir = next((d for d in extract_dir.glob("*.gdb")), None)

        # Baixar e extrair
        try:
            baixar_zip(url, zip_path)
            extrair_zip(zip_path, extract_dir)
            if not gdb_dir:
                gdb_dir = next((d for d in extract_dir.glob("*.gdb")), None)
            if not gdb_dir:
                raise Exception("GDB não encontrado após extração.")
        except Exception as e:
            tqdm.write(f"❌ Falha ao preparar GDB {prefixo}: {e}")
            continue

        # Importar camadas
        for camada in CAMADAS:
            script = IMPORTERS[camada]
            try:
                rodar_importer(script, gdb_dir, camada, distribuidora, ano, prefixo)
            except Exception as e:
                tqdm.write(f"❌ Erro ao rodar {camada} ({prefixo}): {e}")
                continue

    tqdm.write("🏁 Orquestração finalizada.")


if __name__ == "__main__":
    main()
