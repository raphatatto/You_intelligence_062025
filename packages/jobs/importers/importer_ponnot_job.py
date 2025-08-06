import io
import hashlib
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import fiona
import gc

from packages.database.connection import get_db_connection
from packages.jobs.utils.rastreio import registrar_status, gerar_import_id
from packages.jobs.utils.sanitize import sanitize_str, sanitize_numeric, sanitize_int

RELEVANT_COLUMNS = [
    "NOME", "LAT", "LONG", "MUN", "BRR", "CEP", "DESCR"
]

def gerar_pn_id(nome: str, latitude: float, longitude: float, ano: int, dist_id: int) -> str:
    base = f"{nome}_{latitude}_{longitude}_{ano}_{dist_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    if df.empty:
        tqdm.write(f"Nenhum dado para inserir em {table}")
        return 0
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f"Inserido em {table}: {len(df)} registros")
    return len(df)

def importar_ponnot(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, modo_debug: bool = False):
    camada = "PONNOT"
    import_id = gerar_import_id(prefixo, ano, camada)
    registrar_status(prefixo, ano, camada, "running", distribuidora_nome=distribuidora)

    status_final = "failed"
    obs_final = ""
    total_inserted = 0

    try:
        tqdm.write("Abrindo camada com Fiona...")
        with fiona.open(str(gdb_path)) as src:
            layer = next((l for l in src.schema.keys()), "PONNOT")
            dist_id = None
            chunk = []
            chunk_size = 50_000

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    for feature in tqdm(src, desc="Processando registros"):
                        row = feature["properties"]
                        row = {k.upper(): (None if str(v).strip() in ["", "None", "***", "-"] else v) for k, v in row.items()}

                        if dist_id is None:
                            dist_val = sanitize_int(pd.Series([row.get("DIST")])).dropna().unique()
                            if len(dist_val) != 1:
                                raise ValueError(f"Esperado um único código de distribuidora, encontrei: {dist_val}")
                            dist_id = int(dist_val[0])

                        chunk.append(row)
                        if len(chunk) >= chunk_size:
                            inserted = processar_chunk(chunk, cur, import_id, ano, camada, dist_id)
                            total_inserted += inserted
                            conn.commit()
                            chunk = []
                            gc.collect()

                    if chunk:
                        inserted = processar_chunk(chunk, cur, import_id, ano, camada, dist_id)
                        total_inserted += inserted
                        conn.commit()

        if total_inserted == 0:
            status_final = "no_new_rows"
            obs_final = "Nenhum registro válido encontrado."
        else:
            status_final = "completed"
            obs_final = f"{total_inserted} registros inseridos com sucesso."

    except Exception as e:
        tqdm.write(f"Erro na importação do PONNOT: {e}")
        obs_final = str(e)
        if modo_debug:
            raise

    finally:
        registrar_status(
            prefixo, ano, camada, status_final,
            linhas_processadas=total_inserted,
            observacoes=obs_final,
            import_id=import_id,
            distribuidora_nome=distribuidora
        )
        tqdm.write(f"Status final registrado como: {status_final}")

def processar_chunk(chunk_data, cur, import_id, ano, camada, dist_id):
    df = pd.DataFrame(chunk_data)

    df["nome"] = sanitize_str(df.get("NOME"))
    df["latitude"] = sanitize_numeric(df.get("LAT"))
    df["longitude"] = sanitize_numeric(df.get("LONG"))
    df["municipio_id"] = sanitize_int(df.get("MUN"))
    df["bairro"] = sanitize_str(df.get("BRR"))
    df["cep"] = sanitize_int(df.get("CEP"))
    df["descricao"] = sanitize_str(df.get("DESCR"))
    df["pn_id"] = [
        gerar_pn_id(nome, lat, lon, ano, dist_id)
        for nome, lat, lon in zip(df["nome"], df["latitude"], df["longitude"])
    ]
    df["import_id"] = import_id
    df["distribuidora_id"] = dist_id
    df["ano"] = ano
    df["origem"] = camada

    colunas = [
        "pn_id", "import_id", "distribuidora_id", "ano", "origem",
        "nome", "latitude", "longitude", "municipio_id", "bairro", "cep", "descricao"
    ]

    df.dropna(subset=["pn_id"], inplace=True)
    df.drop_duplicates(subset=["pn_id"], inplace=True)

    return insert_copy(cur, df, "ponnot", colunas)

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
