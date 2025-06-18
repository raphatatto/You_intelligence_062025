#!/usr/bin/env python3
"""
Orquestrador de Importações – Youon Intelligence

Executa os jobs de importação UCAT, UCMT, UCBT para uma distribuidora e ano.
Salva o status de cada importação na tabela `import_status`.

Compatível com schema atual:
• distribuidora (PK)
• ano (PK)
• camada
• status
• data_execucao
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from packages.jobs.importers.importer_ucat import importar_ucat
from packages.jobs.importers.importer_ucmt import importar_ucmt
from packages.jobs.importers.importer_ucbt import importar_ucbt
from packages.database.connection import get_db_cursor


def salvar_status(dist: str, ano: int, camada: str, status: str) -> None:
    """Grava/atualiza status do import na tabela import_status."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO import_status
                (distribuidora, ano, camada, status, data_execucao)
            VALUES
                (%s, %s, %s, %s, NOW())
            ON CONFLICT (distribuidora, ano)
            DO UPDATE SET
                camada        = EXCLUDED.camada,
                status        = EXCLUDED.status,
                data_execucao = NOW();
            """,
            (dist, ano, camada, status),
        )


def main():
    # Permite executar com argumentos ou com valores padrão para testes
    if len(sys.argv) >= 3:
        dist = sys.argv[1]
        ano = int(sys.argv[2])
    else:
        dist = "enel distribuição rio"
        ano = 2023

    jobs = {
        "UCAT_tab": importar_ucat,
        "UCMT_tab": importar_ucmt,
        "UCBT_tab": importar_ucbt,
    }

    for camada, job in jobs.items():
        print(f"🚀 Importando {camada} de {dist.upper()} {ano}...")

        gdb_path = Path(f"data/downloads")
        gdb_files = list(gdb_path.glob("*.gdb"))

        if not gdb_files:
            print(f"❌ GDB não encontrada na pasta: {gdb_path}")
            salvar_status(dist, ano, camada, "error")
            continue

        gdb_file = gdb_files[0]

        try:
            job(gdb_file, dist, ano)
            salvar_status(dist, ano, camada, "done")
        except Exception as e:
            print(f"💥 Erro no {camada}: {e}")
            traceback.print_exc()
            salvar_status(dist, ano, camada, "error")


if __name__ == "__main__":
    main()
