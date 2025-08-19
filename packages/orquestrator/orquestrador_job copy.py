import os
import sys
from pathlib import Path
from tqdm import tqdm
from subprocess import run

# Corrige o path base do projeto
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.jobs.utils.rastreio import get_status
from packages.jobs.download.download_gdb import baixar_gdb

# Caminho onde os .gdb são extraídos
DOWNLOADS_DIR = Path("data/downloads")

# Camadas que serão processadas
CAMADAS = ["UCAT", "UCMT", "PONNOT"]
IMPORTERS = {
    "UCAT": "packages/jobs/importers/importer_ucat_job.py",
    "UCMT": "packages/jobs/importers/importer_ucmt_job.py",
    # "UCBT": "packages/jobs/importers/importer_ucbt_job.py",
    "PONNOT": "packages/jobs/importers/importer_ponnot_job.py",
}

# Python atual da venv
PYTHON_EXEC = sys.executable

# Detecta automaticamente os prefixos com base no index JSON
def detectar_prefixos_locais() -> list[str]:
    return [gdb.stem for gdb in DOWNLOADS_DIR.glob("*.gdb")]

def rodar_importer(script_path: str, gdb_path: Path, camada: str, distribuidora: str, ano: int, prefixo: str):
    status = get_status(prefixo, ano, camada)
    if status == "completed":
        tqdm.write(f"✅ Já importado: {camada} {prefixo}")
        return

    tqdm.write(f"⚙️  Importando {camada} para {prefixo}")
    result = run([
        PYTHON_EXEC, script_path,
        "--gdb", str(gdb_path),
        "--ano", str(ano),
        "--distribuidora", distribuidora,
        "--prefixo", prefixo,
        "--modo_debug"
    ],
    capture_output=True,
    text=True,
    env={**os.environ, "PYTHONPATH": str(ROOT)})

    if result.returncode != 0:
        tqdm.write(f"❌ Erro na importação de {camada} ({prefixo}):\n{result.stderr}")
    else:
        tqdm.write(f"✅ {camada} {prefixo} importado com sucesso.")

def main():
    tqdm.write("📁 Iniciando orquestrador inteligente...")

    prefixos = detectar_prefixos_locais()

    # Usa o JSON como fonte oficial dos prefixos válidos
    from json import load
    with open("data/models/aneel_gdb_index.json", encoding="utf-8") as f:
        index = load(f)
    todos_prefixos = list(index.keys())  # Ex: "ENEL_SP_2023"

    for chave in todos_prefixos:
        try:
            distribuidora, ano_str = chave.rsplit("_", 1)
            ano = int(ano_str)
        except Exception:
            tqdm.write(f"⚠️  Prefixo inválido: {chave}")
            continue

        gdb_dir = DOWNLOADS_DIR / f"{chave}.gdb"
        if not gdb_dir.exists():
            try:
                tqdm.write(f"🔍 GDB não encontrado localmente. Tentando baixar {chave}...")
                baixar_gdb(distribuidora, ano)
            except Exception as e:
                tqdm.write(f"❌ Erro ao baixar {chave}: {e}")
                continue

        for camada in CAMADAS:
            script = IMPORTERS[camada]
            try:
                rodar_importer(script, gdb_dir, camada, distribuidora, ano, chave)
            except Exception as e:
                tqdm.write(f"❌ Erro ao importar {camada} ({chave}): {e}")
                continue

    tqdm.write("🏁 Orquestração finalizada com sucesso.")

if __name__ == "__main__":
    main()
