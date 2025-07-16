import io
import csv
import hashlib
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from subprocess import run

from packages.database.connection import get_db_connection
from packages.jobs.utils.rastreio import registrar_status, gerar_import_id
from packages.jobs.utils.sanitize import (
    sanitize_cnae,
    sanitize_grupo_tensao,
    sanitize_modalidade,
    sanitize_tipo_sistema,
    sanitize_situacao,
    sanitize_classe,
    sanitize_pac,
    sanitize_str,
    sanitize_int,
    sanitize_numeric
)

RELEVANT_COLUMNS = [
    "COD_ID", "DIST", "CNAE", "DAT_CON", "PAC", "GRU_TEN", "GRU_TAR", "TIP_SIST",
    "SIT_ATIV", "CLAS_SUB", "CONJ", "MUN", "BRR", "CEP", "PN_CON", "DESCR"
]

def gerar_uc_id(cod_id: str, ano: int, camada: str, distribuidora_id: int) -> str:
    base = f"{cod_id}_{ano}_{camada}_{distribuidora_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f" Inserido em {table}: {len(df)} registros.")

def extrair_csv_ogr(gdb_path: Path, camada: str, output_csv: Path):
    run([
        "ogr2ogr",
        "-f", "CSV",
        str(output_csv),
        str(gdb_path),
        camada
    ], check=True)

def importar_ucbt_ogr(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, modo_debug: bool = False):
    camada = "UCBT"
    import_id = gerar_import_id(prefixo, ano, camada)
    registrar_status(prefixo, ano, camada, "running", distribuidora_nome=distribuidora)

    output_csv = gdb_path.with_suffix(f".{camada.lower()}.csv")

    try:
        tqdm.write(f"Extraindo camada {camada} com ogr2ogr...")
        extrair_csv_ogr(gdb_path, f"{camada}_tab", output_csv)

        linhas_processadas = 0
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for chunk in pd.read_csv(output_csv, chunksize=100_000, dtype=str, na_values=["", "None", "***", "-"]):
                    chunk.columns = chunk.columns.str.upper()
                    for col in RELEVANT_COLUMNS:
                        if col not in chunk.columns:
                            chunk[col] = None

                    dist_id = sanitize_int(chunk["DIST"]).dropna().unique()
                    if len(dist_id) != 1:
                        raise ValueError(f"Esperado um único código de distribuidora, mas encontrei: {dist_id}")
                    dist_id = int(dist_id[0])

                    chunk["uc_id"] = [
                        gerar_uc_id(cod, ano, camada, dist_id)
                        for cod in chunk["COD_ID"]
                    ]
                    chunk["import_id"] = import_id
                    chunk["distribuidora_id"] = dist_id
                    chunk["origem"] = camada
                    chunk["ano"] = ano
                    chunk["status"] = "raw"
                    chunk["data_conexao"] = pd.to_datetime(chunk["DAT_CON"], errors="coerce")
                    chunk["cnae"] = sanitize_cnae(chunk["CNAE"])
                    chunk["grupo_tensao"] = chunk["GRU_TEN"].apply(sanitize_grupo_tensao)
                    chunk["modalidade"] = chunk["GRU_TAR"].apply(sanitize_modalidade)
                    chunk["tipo_sistema"] = chunk["TIP_SIST"].apply(sanitize_tipo_sistema)
                    chunk["situacao"] = chunk["SIT_ATIV"].apply(sanitize_situacao)
                    chunk["classe"] = chunk["CLAS_SUB"].apply(sanitize_classe)
                    chunk["segmento"] = None
                    chunk["subestacao"] = sanitize_str(chunk.get("SUB"))
                    chunk["municipio_id"] = sanitize_int(chunk["MUN"])
                    chunk["bairro"] = sanitize_str(chunk["BRR"])
                    chunk["cep"] = sanitize_int(chunk["CEP"])
                    chunk["pac"] = chunk["PAC"].apply(sanitize_pac)
                    chunk["pn_con"] = sanitize_str(chunk["PN_CON"])
                    chunk["descricao"] = sanitize_str(chunk["DESCR"])

                    df_bruto = chunk[[
                        "uc_id", "import_id", "COD_ID", "distribuidora_id", "origem", "ano", "status", "data_conexao",
                        "cnae", "grupo_tensao", "modalidade", "tipo_sistema", "situacao", "classe", "segmento",
                        "subestacao", "municipio_id", "bairro", "cep", "pac", "pn_con", "descricao"
                    ]].rename(columns={"COD_ID": "cod_id"})

                    df_bruto.drop_duplicates(subset="uc_id", inplace=True)
                    insert_copy(cur, df_bruto, "lead_bruto", df_bruto.columns.tolist())
                    conn.commit()
                    linhas_processadas += len(df_bruto)

        # Pós-inserção: puxar IDs para foreign key
        df_ids = pd.read_sql("""
            SELECT id AS lead_bruto_id, uc_id FROM lead_bruto WHERE import_id = %s
        """, conn, params=(import_id,))

        # Segunda rodada para inserir energia e qualidade
        for chunk in pd.read_csv(output_csv, chunksize=100_000, dtype=str, na_values=["", "None", "***", "-"]):
            chunk.columns = chunk.columns.str.upper()
            chunk["uc_id"] = [
                gerar_uc_id(cod, ano, camada, dist_id)
                for cod in chunk["COD_ID"]
            ]
            df_energy = []
            df_qual = []
            for mes in range(1, 13):
                df_energy.append(pd.DataFrame({
                    "uc_id": chunk["uc_id"],
                    "mes": mes,
                    "energia_ponta": None,
                    "energia_fora_ponta": None,
                    "energia_total": sanitize_numeric(chunk.get(f"ENE_{mes:02d}")),
                    "origem": camada
                }))
                df_qual.append(pd.DataFrame({
                    "uc_id": chunk["uc_id"],
                    "mes": mes,
                    "dic": sanitize_numeric(chunk.get(f"DIC_{mes:02d}")),
                    "fic": sanitize_numeric(chunk.get(f"FIC_{mes:02d}")),
                    "sem_rede": sanitize_numeric(chunk.get("SEMRED")),
                    "origem": camada
                }))
            df_energia = pd.concat(df_energy).reset_index(drop=True)
            df_qualidade = pd.concat(df_qual).reset_index(drop=True)

            df_energia = df_energia.merge(df_ids, on="uc_id").drop(columns=["uc_id"])
            df_qualidade = df_qualidade.merge(df_ids, on="uc_id").drop(columns=["uc_id"])

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    insert_copy(cur, df_energia, "lead_energia_mensal", df_energia.columns.tolist())
                    insert_copy(cur, df_qualidade, "lead_qualidade_mensal", df_qualidade.columns.tolist())
                conn.commit()

        registrar_status(
            prefixo, ano, camada, "completed",
            linhas_processadas=linhas_processadas,
            import_id=import_id
        )
        tqdm.write("✅ Importação UCBT via ogr2ogr finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f"❌ Erro na importação UCBT via ogr2ogr: {e}")
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

    importar_ucbt_ogr(
        gdb_path=args.gdb,
        distribuidora=args.distribuidora,
        ano=args.ano,
        prefixo=args.prefixo,
        modo_debug=args.modo_debug
    )
