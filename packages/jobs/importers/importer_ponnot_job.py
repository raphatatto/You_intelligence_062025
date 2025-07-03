# packages/jobs/importers/importer_ponnot_job.py

import geopandas as gpd
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from psycopg2.extras import execute_batch
from fiona import listlayers

from packages.database.connection import get_db_cursor
from packages.jobs.utils.rastreio import registrar_status

# Detecta dinamicamente a layer com prefixo “PONNOT”
def _detect_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next(l for l in layers if l.upper().startswith("PONNOT"))

BATCH_SIZE = 10_000

def _chunkify(df: pd.DataFrame, size: int = BATCH_SIZE):
    records = df.to_dict("records")
    for i in range(0, len(records), size):
        yield records[i : i + size]

def main(
    gdb_path: Path,
    distribuidora: str,  # não usado aqui, mas mantido na assinatura
    ano: int,
    prefixo: str,
    camada: str = "PONNOT",
    modo_debug: bool = False,
):
    registrar_status(prefixo, ano, camada, "started")
    try:
        # 1) detecta layer
        layer = _detect_layer(gdb_path)
        tqdm.write(f"📖 Lendo camada '{layer}' do GDB em {gdb_path}...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)
        total = len(gdf)
        tqdm.write(f"   → {total} feições encontradas.")

        if total == 0:
            tqdm.write("   → Nenhuma feição; marcando no_new_rows.")
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return

        # 2) monta DataFrame com coordenadas
        df = pd.DataFrame({
            "pn_id":     gdf["COD_ID"],
            "latitude":  gdf.geometry.y,
            "longitude": gdf.geometry.x,
        })

        sql_insert = """
            INSERT INTO ponto_notavel (pn_id, latitude, longitude)
            VALUES (%(pn_id)s, %(latitude)s, %(longitude)s)
            ON CONFLICT (pn_id) DO NOTHING
        """

        # 3) insere em batches
        with get_db_cursor(commit=True) as cur:
            for batch in tqdm(_chunkify(df), desc="PONNOT_batches", unit="batch"):
                execute_batch(cur, sql_insert, batch)
            tqdm.write("✅ ponto_notavel inserido")

        registrar_status(prefixo, ano, camada, "success")

    except Exception as e:
        tqdm.write(f"❌ Erro na importação PONNOT: {e}")
        registrar_status(prefixo, ano, camada, f"failed: {e}")
        if modo_debug:
            raise
