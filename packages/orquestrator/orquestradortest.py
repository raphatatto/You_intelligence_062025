# packages/orquestrator/orquestrador_teste.job.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime
from packages.jobs.importers.importer_ucmt import importar_ucmt
from packages.jobs.importers.importer_ucat import importar_ucat
from packages.jobs.importers.importer_ucbt import importar_ucbt
from packages.database.connection import get_db_cursor

# ─── PASTA EXTRAÍDA ───────────────────────────────────────────

DOWNLOAD_FOLDER = Path("data/downloads")

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

# ─── EXECUÇÃO DO ORQUESTRADOR ────────────────────────────────

def main():
    datasets = [
        {
            "distribuidora": "enel distribuição rio",
            "ano": 2023,
            "folder": "Enel_RJ_383_2023-12-31_V11_20250112-1903.gdb"
        },
        {
            "distribuidora": "enel distribuição são paulo",
            "ano": 2023,
            "folder": "Enel_SP_390_2023-12-31_V11_20250108-0947.gdb"
        },
        {
            "distribuidora": "light",
            "ano": 2023,
            "folder": "Light_382_2023-12-31_V11_20240116-1348.gdb"
        },
        {
            "distribuidora": "neoenergia elektro",
            "ano": 2023,
            "folder": "Neoenergia_Elektro_385_2022-12-31_V11_20231110-1655.gdb"
        },
        {
            "distribuidora": "cpfl paulista",
            "ano": 2023,
            "folder": "CPFL_Paulista_63_2023-12-31_V11_20241223-0817.gdb"
        }
    ]

    camada_jobs = {
        "UCMT_tab": importar_ucmt,
        "UCBT_tab": importar_ucbt,
        "UCAT_tab": importar_ucat,
    }

    for item in datasets:
        distribuidora = item["distribuidora"].lower()
        ano = item["ano"]
        folder_name = item["folder"]
        gdb_path = DOWNLOAD_FOLDER / folder_name

        if not gdb_path.exists():
            print(f"❌ Pasta GDB não encontrada: {gdb_path}")
            continue

        for camada, job_func in camada_jobs.items():
            if ja_importado(distribuidora, ano, camada):
                print(f"✅ {camada} já importada para {distribuidora} {ano}, pulando...")
                continue
            try:
                print(f"🚀 Importando {camada} de {distribuidora.upper()} {ano}...")
                job_func(gdb_path, distribuidora, ano)
                salvar_status(distribuidora, ano, camada, "success")
            except Exception as err:
                print(f"❌ Erro ao importar {camada}: {err}")
                salvar_status(distribuidora, ano, camada, "error")

if __name__ == "__main__":
    main()
