import os
import sys
from pathlib import Path
from tqdm import tqdm
from subprocess import run

# Corrige o path base do projeto para execução direta
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# IMPORT CORRETO do rastreio (no seu repo não há "utils.rastreio")
from packages.jobs.utils.rastreio import get_status

# Pasta onde estão os .gdb
DOWNLOADS_DIR = Path("data/downloads")

# Detecta todos os arquivos .gdb automaticamente
PREFIXOS = [gdb.stem for gdb in DOWNLOADS_DIR.glob("*.gdb")]

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


def _build_args(camada: str, gdb_path: Path, distribuidora: str, ano: int, prefixo: str) -> list[str]:
    """
    UCAT/UCMT usam --prefixo; UCBT/PONNOT não.
    Todos aceitam --modo-debug (com hífen).
    """
    base = ["--gdb", str(gdb_path), "--distribuidora", distribuidora, "--ano", str(ano)]
    if camada in ("UCAT", "UCMT"):
        return base + ["--prefixo", prefixo, "--modo-debug"]
    else:
        return base + ["--modo-debug"]


def rodar_importer(
    script_path: str, gdb_path: Path, camada: str, distribuidora: str, ano: int, prefixo: str
):
    status = get_status(prefixo, ano, camada)
    if status == "completed":
        tqdm.write(f"[OK] Ja importado: {camada} {prefixo}")
        return

    args = _build_args(camada, gdb_path, distribuidora, ano, prefixo)
    tqdm.write(f"[RUN] Importando {camada} para {prefixo}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    result = run([PYTHON_EXEC, script_path] + args, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        tqdm.write(f"[ERR] Importacao falhou {camada} ({prefixo})")
        if result.stderr:
            tqdm.write(result.stderr)
        else:
            tqdm.write("Sem stderr. Verifique logs do importer.")
    else:
        tqdm.write(f"[DONE] {camada} {prefixo} importado com sucesso.")
        if result.stdout:
            # opcional: mostrar um resumo do stdout
            out = result.stdout.strip()
            if out:
                tqdm.write(out.splitlines()[-1])


def orquestrar_importacao():
    tqdm.write("[INFO] Iniciando orquestrador manual (mock)")

    for prefixo in PREFIXOS:
        gdb_dir = DOWNLOADS_DIR / f"{prefixo}.gdb"

        if not gdb_dir.exists():
            tqdm.write(f"[WARN] .gdb nao encontrado: {gdb_dir}")
            continue

        try:
            distribuidora = prefixo.rsplit("_", 1)[0]
            ano = int(prefixo.rsplit("_", 1)[-1])
        except Exception:
            tqdm.write(f"[WARN] Prefixo invalido: {prefixo} — use formato NOME_UF_2023")
            continue

        for camada in CAMADAS:
            script = IMPORTERS[camada]
            try:
                rodar_importer(script, gdb_dir, camada, distribuidora, ano, prefixo)
            except Exception as e:
                tqdm.write(f"[ERR] Erro ao rodar {camada} ({prefixo}): {e}")
                continue

    tqdm.write("[INFO] Orquestracao mock finalizada.")


if __name__ == "__main__":
    orquestrar_importacao()
