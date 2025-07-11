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

# Caminho para a pasta onde estão os .gdb
DOWNLOADS_DIR = Path("data/downloads")

# Detecta todos os arquivos .gdb automaticamente
PREFIXOS = [
    gdb.stem for gdb in DOWNLOADS_DIR.glob("*.gdb")
]

# Camadas a importar
CAMADAS = ["UCAT", "UCMT", "UCBT", "PONNOT"]
IMPORTERS = {
    "UCAT": "packages/jobs/importers/importer_ucat_job.py",
    "UCMT": "packages/jobs/importers/importer_ucmt_job.py",
    "UCBT": "packages/jobs/importers/importer_ucbt_job.py",
    "PONNOT": "packages/jobs/importers/importer_ponnot_job.py",
}

# Usa o Python atual da venv para rodar subprocessos
PYTHON_EXEC = sys.executable

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
    tqdm.write("📁 Iniciando orquestrador manual (mock)")

    for prefixo in PREFIXOS:
        gdb_dir = DOWNLOADS_DIR / f"{prefixo}.gdb"

        if not gdb_dir.exists():
            tqdm.write(f"❌ .gdb não encontrado: {gdb_dir}")
            continue

        try:
            distribuidora = prefixo.rsplit("_", 1)[0]
            ano = int(prefixo.rsplit("_", 1)[-1])
        except Exception:
            tqdm.write(f"⚠️  Prefixo inválido: {prefixo} — use formato NOME_UF_2023")
            continue

        for camada in CAMADAS:
            script = IMPORTERS[camada]
            try:
                rodar_importer(script, gdb_dir, camada, distribuidora, ano, prefixo)
            except Exception as e:
                tqdm.write(f"❌ Erro ao rodar {camada} ({prefixo}): {e}")
                continue

    tqdm.write("🏁 Orquestração mock finalizada.")

if __name__ == "__main__":
    main()
