import io
import csv
import gc
import hashlib
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import fiona

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

def importar_ucbt_fiona(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, modo_debug: bool = False):
    camada = "UCBT"
    import_id = gerar_import_id(prefixo, ano, camada)
    registrar_status(prefixo, ano, camada, "running", distribuidora_nome=distribuidora)

    try:
        tqdm.write(" Abrindo camada 'UCBT_tab' com Fiona...")
        with fiona.open(str(gdb_path), layer="UCBT_tab") as src:
            dist_id = None
            chunk_size = 100_000
            chunk = []

            total_inserted = 0
            all_uc_ids = []
            all_rows = []

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    for feature in tqdm(src, desc=" Processando registros"):
                        row = feature["properties"]
                        row = {k.upper(): (None if str(v).strip() in ["", "None", "***", "-"] else v) for k, v in row.items()}
                        all_rows.append(row)

                        if dist_id is None:
                            dist_val = sanitize_int(pd.Series([row.get("DIST")])).dropna().unique()
                            if len(dist_val) != 1:
                                raise ValueError(f"Esperado um único código de distribuidora, encontrei: {dist_val}")
                            dist_id = int(dist_val[0])

                        chunk.append(row)
                        if len(chunk) >= chunk_size:
                            total_inserted += processar_chunk(chunk, cur, import_id, ano, camada, dist_id, all_uc_ids)
                            conn.commit()
                            chunk = []
                            gc.collect()

                    if chunk:
                        total_inserted += processar_chunk(chunk, cur, import_id, ano, camada, dist_id, all_uc_ids)
                        conn.commit()
                        gc.collect()

            tqdm.write(" Gerando dados mensais (energia, qualidade, demanda)...")

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    df_ids = pd.read_sql("""
                        SELECT id AS lead_bruto_id, uc_id FROM lead_bruto WHERE import_id = %s
                    """, conn, params=(import_id,))
                    ucid_map = df_ids.set_index("uc_id")["lead_bruto_id"].to_dict()

                    energia_data, qualidade_data, demanda_data = [], [], []

                    for row in tqdm(all_rows, desc=" Mensais"):
                        cod_id = row.get("COD_ID")
                        uc_id = gerar_uc_id(cod_id, ano, camada, dist_id)
                        lead_bruto_id = ucid_map.get(uc_id)
                        if not lead_bruto_id:
                            continue

                        for mes in range(1, 13):
                            energia_data.append({
                                "lead_bruto_id": lead_bruto_id,
                                "mes": mes,
                                "energia_ponta": None,
                                "energia_fora_ponta": None,
                                "energia_total": sanitize_numeric(row.get(f"ENE_{mes:02d}")),
                                "origem": camada,
                                "import_id": import_id
                            })
                            qualidade_data.append({
                                "lead_bruto_id": lead_bruto_id,
                                "mes": mes,
                                "dic": sanitize_numeric(row.get(f"DIC_{mes:02d}")),
                                "fic": sanitize_numeric(row.get(f"FIC_{mes:02d}")),
                                "sem_rede": sanitize_numeric(row.get("SEMRED")),
                                "origem": camada,
                                "import_id": import_id
                            })
                            demanda_data.append({
                                "lead_bruto_id": lead_bruto_id,
                                "mes": mes,
                                "demanda_ponta": None,
                                "demanda_fora_ponta": None,
                                "demanda_total": sanitize_numeric(row.get(f"DEM_{mes:02d}")),
                                "demanda_contratada": sanitize_numeric(row.get("DEM_CONT")),
                                "origem": camada,
                                "import_id": import_id
                            })

                    insert_copy(cur, pd.DataFrame(energia_data), "lead_energia_mensal", list(energia_data[0].keys()))
                    insert_copy(cur, pd.DataFrame(qualidade_data), "lead_qualidade_mensal", list(qualidade_data[0].keys()))
                    insert_copy(cur, pd.DataFrame(demanda_data), "lead_demanda_mensal", list(demanda_data[0].keys()))
                conn.commit()

            registrar_status(
                prefixo, ano, camada, "completed",
                linhas_processadas=total_inserted,
                import_id=import_id,
                observacoes=f"{len(energia_data)} energia | {len(demanda_data)} demanda | {len(qualidade_data)} qualidade"
            )
            tqdm.write(" Importação UCBT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f" Erro na importação de UCBT: {e}")
        registrar_status(prefixo, ano, camada, "failed", erro=str(e), import_id=import_id)
        if modo_debug:
            raise

def processar_chunk(chunk_data, cur, import_id, ano, camada, dist_id, all_uc_ids):
    df = pd.DataFrame(chunk_data)

    df = df[df["COD_ID"].notna()]
    for col in RELEVANT_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df["uc_id"] = [
        gerar_uc_id(cod, ano, camada, dist_id)
        for cod in df["COD_ID"]
    ]
    all_uc_ids.extend(df["uc_id"].tolist())

    df["cod_id"] = df["COD_ID"]
    df["import_id"] = import_id
    df["distribuidora_id"] = dist_id
    df["origem"] = camada
    df["ano"] = ano
    df["status"] = "raw"
    df["data_conexao"] = pd.to_datetime(df["DAT_CON"], dayfirst=True, errors="coerce")
    df["cnae"] = sanitize_cnae(df["CNAE"].astype(str).fillna(""))
    df["grupo_tensao"] = df["GRU_TEN"].apply(sanitize_grupo_tensao)
    df["modalidade"] = df["GRU_TAR"].apply(sanitize_modalidade)
    df["tipo_sistema"] = df["TIP_SIST"].apply(sanitize_tipo_sistema)
    df["situacao"] = df["SIT_ATIV"].apply(sanitize_situacao)
    df["classe"] = df["CLAS_SUB"].apply(sanitize_classe)
    df["segmento"] = None
    df["subestacao"] = None
    df["municipio_id"] = sanitize_int(df["MUN"])
    df["bairro"] = sanitize_str(df["BRR"])
    df["cep"] = sanitize_int(df["CEP"])
    df["pac"] = df["PAC"].apply(sanitize_pac)
    df["pn_con"] = sanitize_str(df["PN_CON"])
    df["descricao"] = sanitize_str(df["DESCR"])

    df.drop_duplicates(subset="uc_id", inplace=True)

    colunas_validas = [
        "uc_id", "import_id", "cod_id", "distribuidora_id", "origem", "ano", "status",
        "data_conexao", "cnae", "grupo_tensao", "modalidade", "tipo_sistema", "situacao",
        "classe", "segmento", "subestacao", "municipio_id", "bairro", "cep", "pac",
        "pn_con", "descricao"
    ]
    df = df[colunas_validas]

    insert_copy(cur, df, "lead_bruto", colunas_validas)
    return len(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gdb", required=True, type=Path)
    parser.add_argument("--ano", required=True, type=int)
    parser.add_argument("--distribuidora", required=True)
    parser.add_argument("--prefixo", required=True)
    parser.add_argument("--modo_debug", action="store_true")
    args = parser.parse_args()

    importar_ucbt_fiona(
        gdb_path=args.gdb,
        distribuidora=args.distribuidora,
        ano=args.ano,
        prefixo=args.prefixo,
        modo_debug=args.modo_debug
    )
