import subprocess
from pathlib import Path
import sys
import os

# Define o diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PYTHON_EXECUTAVEL = sys.executable

# Lista de scripts de diagnóstico (com caminho absoluto)
SCRIPTS = [
    ROOT_DIR / "packages" / "jobs" / "diagnostico" / "estruturar_banco_job.py",
    ROOT_DIR / "packages" / "jobs" / "diagnostico" / "documentar_banco_job.py",
    ROOT_DIR / "packages" / "jobs" / "diagnostico" / "recomendar_melhorias_job.py"
]

def run_script(script_path: Path):
    print(f"\n🚀 Executando: {script_path.name}...")

    result = subprocess.run(
        [PYTHON_EXECUTAVEL, str(script_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT_DIR)}  # 🔥 ESSENCIAL
    )

    if result.returncode != 0:
        print(f"❌ Erro ao rodar {script_path.name}")
        print(result.stderr)
    else:
        print(f"✅ {script_path.name} finalizado com sucesso!")
        print(result.stdout)

if __name__ == "__main__":
    print("📊 Iniciando pipeline de diagnóstico do banco...")
    for script in SCRIPTS:
        run_script(script)
    print("\n🏁 Diagnóstico completo.")
