# orquestrador.py
#!/usr/bin/env python3
import sys
import asyncio
import logging
from pathlib import Path
from tqdm import tqdm

# Logging via tqdm
class TqdmLoggingHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.addHandler(TqdmLoggingHandler())

# Permitir imports a partir da raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from packages.jobs.utils.rastreio import registrar_status, get_status
from packages.jobs.importers.importer_ucat_job import main as importar_ucat
from packages.jobs.importers.importer_ucmt_job import main as importar_ucmt
from packages.jobs.importers.importer_ucbt_job import main as importar_ucbt
from packages.jobs.importers.importer_ponnot_job import main as importar_ponnot

# Onde estão os GDBs extraídos
gdb_root = Path("data/downloads")
BASES = {
    "UCAT_tab": importar_ucat,
    "UCMT_tab": importar_ucmt,
    "UCBT_tab": importar_ucbt,
    "PONNOT":   importar_ponnot,
}


def encontrar_gdb(prefixo: str, ano: int) -> Path | None:
    candidatos = list(gdb_root.glob(f"{prefixo}_{ano}*.gdb"))
    return candidatos[0] if candidatos else None


async def importar_distribuidora(nome: str, prefixo: str, ano: int):
    gdb = encontrar_gdb(prefixo, ano)
    if not gdb:
        logger.warning(f"GDB não encontrado: {prefixo} {ano}")
        registrar_status(prefixo, ano, camada="ALL", status="gdb_not_found")
        return

    logger.info(f"Usando GDB: {gdb.name}")
    for camada, importer in BASES.items():
        prev = get_status(prefixo, ano, camada)
        if prev == "success":
            logger.info(f"[{camada}] já concluída, pulando.")
            continue

        logger.info(f"🔄 Iniciando importação: {camada} | {nome} {ano}")
        registrar_status(prefixo, ano, camada, "started")
        try:
            importer(
                gdb_path=gdb,
                distribuidora=nome,
                ano=ano,
                prefixo=prefixo,
                camada=camada,
                modo_debug=False
            )
        except Exception as e:
            logger.error(f"❌ Erro em {camada}: {e}", exc_info=True)
            registrar_status(prefixo, ano, camada, f"failed: {e}")
            continue

        final = get_status(prefixo, ano, camada)
        if final is None:
            logger.error(f"[{camada}] sem status final registrado!")
        else:
            logger.info(f"✅ {camada} finalizado com status '{final}'")


async def rodar_orquestrador(selecionados: list[dict]):
    for item in selecionados:
        await importar_distribuidora(item["nome"], item["prefixo"], item["ano"])


if __name__ == "__main__":
    DISTRIBUIDORAS = [
        # {"nome": "CPFL PAULISTA",         "prefixo": "CPFL_Paulista_63",   "ano": 2023},
        {"nome": "ENEL DISTRIBUIÇÃO RIO", "prefixo": "Enel_RJ_383",         "ano": 2023},
        # ... outros
    ]
    asyncio.run(rodar_orquestrador(DISTRIBUIDORAS))