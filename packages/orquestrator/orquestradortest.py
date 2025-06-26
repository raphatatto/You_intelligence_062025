import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# from packages.jobs.importers.importer_ucat import main as importar_ucat
from packages.jobs.importers.importer_ucmt import main as importar_ucmt
from packages.jobs.importers.importer_ucbt import main as importar_ucbt

# Parâmetros de execução
DISTRIBUIDORAS = {
    "ENEL DISTRIBUIÇÃO RIO": "Enel_RJ_383",
    "CPFL PAULISTA": "CPFL_Paulista_63",
    # adicione outras distribuidoras aqui
}

ANOS = [2023]

BASES = {
    # "UCAT": {"main": importar_ucat, "layer": "UCAT_tab"},
    "UCMT": { "main": importar_ucmt, "layer": "UCMT_tab" },
    # "UCBT": { "main": importar_ucbt, "layer": "UCBT_tab" }
}

GDB_DIR = Path("data/downloads")  # onde estão os arquivos GDB

def encontrar_gdb(prefixo: str, ano: int) -> Path | None:
    candidatos = list(GDB_DIR.glob(f"{prefixo}_{ano}*.gdb"))
    return candidatos[0] if candidatos else None

async def rodar_importacoes():
    for dist_nome, prefixo in DISTRIBUIDORAS.items():
        for ano in ANOS:
            gdb = encontrar_gdb(prefixo, ano)
            if not gdb:
                print(f"⚠️  GDB não encontrada para {dist_nome} {ano}")
                continue

            for base, config in BASES.items():
                print(f"🔄 Iniciando importação: {base} | {dist_nome} {ano}")
                try:
                    config["main"](gdb_path=gdb, distribuidora=dist_nome, ano=ano, camada=config["layer"])

                except Exception as e:
                    print(f"❌ Erro em {base} - {dist_nome}: {e}")

if __name__ == "__main__":
    asyncio.run(rodar_importacoes())
