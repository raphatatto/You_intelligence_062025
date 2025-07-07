import os
import io
import hashlib
import argparse
import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm
from fiona import listlayers

from packages.database.connection import get_db_connection
from packages.jobs.utils.rastreio import registrar_status, gerar_import_id


def detectar_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith("PONNOT")), None)


def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f"✅ Inserido em {table}: {len(df)} registros.")


def importar_ponnot(
    gdb_path: Path,
    distribuidora: str,
    ano: int,
    prefixo: str,
    modo_debug: bool = False
):
    camada = "PONNOT"
    registrar_status(prefixo, ano, camada, "started")
    import_id = gerar_import_id(prefixo, ano, camada)

    try:
        layer = detectar_layer(gdb_path)
        if not layer:
            raise Exception("Camada PONNOT não encontrada no GDB.")

        tqdm.write(f"📖 Lendo camada '{layer}'...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

        if len(gdf) == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return

        # Gera DataFrame com coordenadas e pn_id
        tqdm.write("🧭 Extraindo coordenadas...")
        df = pd.DataFrame({
            "pn_id": gdf["COD_ID"],
            "latitude": gdf.geometry.y,
            "longitude": gdf.geometry.x
        })

        conn = get_db_connection()
        with conn.cursor() as cur:
            insert_copy(cur, df, "ponto_notavel", ["pn_id", "latitude", "longitude"])
        conn.commit()

        registrar_status(prefixo, ano, camada, "success")
        tqdm.write("🎉 Importação PONNOT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f"❌ Erro ao importar PONNOT: {e}")
        registrar_status(prefixo, ano, camada, f"failed: {e}")
        if modo_debug:
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gdb", required=True, type=Path)
    parser.add_argument("--ano", required=True, type=int)
    parser.add_argument("--distribuidora", required=True)
    parser.add_argument("--prefixo", required=True)
    parser.add_argument("--modo_debug", action="store_true")

    args = parser.parse_args()

    importar_ponnot(
        gdb_path=args.gdb,
        distribuidora=args.distribuidora,
        ano=args.ano,
        prefixo=args.prefixo,
        modo_debug=args.modo_debug
    )
