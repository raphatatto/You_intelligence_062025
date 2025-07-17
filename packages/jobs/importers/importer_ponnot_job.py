import io
import argparse
import hashlib
import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm
from fiona import listlayers

from packages.database.connection import get_db_connection
from packages.jobs.utils.rastreio import registrar_status, gerar_import_id
from packages.jobs.utils.sanitize import sanitize_int, sanitize_str, sanitize_numeric


RELEVANT_COLUMNS = ["ID", "MUN", "NOME", "LAT", "LONG", "DESCR", "CEP"]

def detectar_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith("PONNOT")), None)

def gerar_pn_id(pn_nome: str, latitude: float, longitude: float, ano: int, dist_id: int) -> str:
    base = f"{pn_nome}_{latitude}_{longitude}_{ano}_{dist_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f" Inserido em {table}: {len(df)} registros.")

def importar_ponnot(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, modo_debug: bool = False):
    camada = "PONNOT"
    import_id = gerar_import_id(prefixo, ano, camada)
    registrar_status(prefixo, ano, camada, "running", distribuidora_nome=distribuidora)

    try:
        layer = detectar_layer(gdb_path)
        if not layer:
            raise Exception("Camada PONNOT não encontrada no GDB.")

        tqdm.write(f" Lendo camada '{layer}'...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

        if len(gdf) == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows", import_id=import_id)
            return

        gdf.replace(["None", "nan", "", "***", "-"], None, inplace=True)

        for col in RELEVANT_COLUMNS:
            if col not in gdf.columns:
                gdf[col] = None

        tqdm.write(" Transformando PONNOT para DataFrame...")

        # Verifica se a coluna ID (DIST) é válida
        dist_ids = sanitize_int(gdf["ID"]).dropna().unique()
        if len(dist_ids) != 1:
            tqdm.write(f"⚠️  Coluna 'ID' está vazia ou possui múltiplos códigos em PONNOT {prefixo}. Pulando importação.")
            registrar_status(prefixo, ano, camada, "skipped", import_id=import_id, observacoes="ID inválido em PONNOT")
            return

        dist_id = int(dist_ids[0])

        df_pn = pd.DataFrame({
            "pn_id": [
                gerar_pn_id(row["NOME"], row["LAT"], row["LONG"], ano, dist_id)
                for _, row in gdf.iterrows()
            ],
            "import_id": import_id,
            "nome": sanitize_str(gdf["NOME"]),
            "municipio_id": sanitize_int(gdf["MUN"]),
            "latitude": sanitize_numeric(gdf["LAT"]),
            "longitude": sanitize_numeric(gdf["LONG"]),
            "descricao": sanitize_str(gdf["DESCR"]),
            "cep": sanitize_int(gdf["CEP"]),
        })

        df_pn = df_pn[df_pn["pn_id"].notnull()].drop_duplicates(subset=["pn_id"]).reset_index(drop=True)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                insert_copy(cur, df_pn, "ponto_notavel", df_pn.columns.tolist())
            conn.commit()

        registrar_status(
            prefixo, ano, camada, "completed",
            linhas_processadas=len(df_pn),
            import_id=import_id,
            observacoes=f"{len(df_pn)} pontos notáveis"
        )
        tqdm.write(" Importação PONNOT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f" Erro ao importar PONNOT: {e}")
        registrar_status(prefixo, ano, camada, "failed", erro=str(e), import_id=import_id)
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
