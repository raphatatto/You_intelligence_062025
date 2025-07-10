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
    tqdm.write(f"🔍 Layers disponíveis: {layers}")
    return next((l for l in layers if l.upper().startswith("PONNOT")), None)


def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    try:
        tqdm.write(f"📦 Iniciando inserção de {len(df)} registros na tabela {table}...")
        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
        buf.seek(0)
        cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
        tqdm.write(f"✅ Inserido com sucesso em {table}.")
    except Exception as e:
        tqdm.write(f"❌ Falha ao inserir no banco: {e}")
        raise


def importar_ponnot(
    gdb_path: Path,
    distribuidora: str,
    ano: int,
    prefixo: str,
    modo_debug: bool = False
):
    camada = "PONNOT"
    tqdm.write(f"🚀 Iniciando importação PONNOT | Distribuidora: {distribuidora} | Ano: {ano} | GDB: {gdb_path.name}")
    registrar_status(prefixo, ano, camada, "running")
    import_id = gerar_import_id(prefixo, ano, camada)

    try:
        layer = detectar_layer(gdb_path)
        if not layer:
            raise Exception("Camada PONNOT não encontrada no GDB.")

        tqdm.write(f"📖 Lendo camada '{layer}' do arquivo {gdb_path.name}...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

        if gdf.empty:
            tqdm.write("⚠️ Camada está vazia!")
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return

        if "COD_ID" not in gdf.columns:
            raise Exception("Coluna 'COD_ID' não encontrada na camada PONNOT.")

        tqdm.write(f"🧭 Extraindo {len(gdf)} coordenadas...")
        df = pd.DataFrame({
            "pn_id": gdf["COD_ID"].astype(str),
            "latitude": gdf.geometry.y,
            "longitude": gdf.geometry.x,
            "distribuidora_id": distribuidora,
            "ano": ano
        })

        df = df.drop_duplicates(subset=["pn_id", "distribuidora_id", "ano"])
        df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
        tqdm.write(f"📉 Após limpeza: {len(df)} registros únicos com coordenadas válidas.")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                insert_copy(
                    cur,
                    df,
                    "ponto_notavel",
                    ["pn_id", "latitude", "longitude", "distribuidora_id", "ano"]
                )
            conn.commit()

        registrar_status(prefixo, ano, camada, "completed")
        tqdm.write("🎉 Importação PONNOT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f"❌ Erro ao importar PONNOT: {e}")
        registrar_status(prefixo, ano, camada, "failed", erro=str(e))
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
