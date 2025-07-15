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

def detectar_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith("UCBT")), None)

def gerar_uc_id(cod_id: str, ano: int, camada: str, distribuidora_id: int) -> str:
    base = f"{cod_id}_{ano}_{camada}_{distribuidora_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f" Inserido em {table}: {len(df)} registros.")

def importar_ucbt(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, modo_debug: bool = False):
    camada = "UCBT"
    import_id = gerar_import_id(prefixo, ano, camada)
    registrar_status(prefixo, ano, camada, "running", distribuidora_nome=distribuidora)

    try:
<<<<<<< HEAD
        layer = detectar_layer(gdb_path)
        if not layer:
            raise Exception("Camada UCBT não encontrada no GDB.")

        tqdm.write(f" Lendo camada '{layer}'...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

=======
        tqdm.write(" Verificando camadas no GDB...")
        layer = detectar_layer(gdb_path, camada)
        if not layer:
            raise Exception("Camada UCBT não encontrada no GDB.")

        tqdm.write(f" Lendo camada real '{layer}'...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

        #  Normalizar colunas para evitar erros com capitalização e espaços
        gdf.columns = [col.strip().upper() for col in gdf.columns]
        tqdm.write(f" Colunas disponíveis: {list(gdf.columns)}")

        if "COD_ID" not in gdf.columns:
            raise KeyError(" A coluna 'COD_ID' não foi encontrada no DataFrame após leitura do GDB.")

>>>>>>> 56e553dd86508d8dc28552b23dc773f6d22225a1
        if len(gdf) == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows", import_id=import_id)
            return

        gdf.replace(["None", "nan", "", "***", "-"], None, inplace=True)

        for col in RELEVANT_COLUMNS:
            if col not in gdf.columns:
                gdf[col] = None

        tqdm.write(" Transformando UCBT para lead_bruto...")

<<<<<<< HEAD
        dist_id = sanitize_int(gdf["DIST"]).dropna().unique()
        if len(dist_id) != 1:
            raise ValueError(f"Esperado um único código de distribuidora, mas encontrei: {dist_id}")
        dist_id = int(dist_id[0])
=======
        tqdm.write(" Montando campos mensais...")
>>>>>>> 56e553dd86508d8dc28552b23dc773f6d22225a1

        df_bruto = pd.DataFrame({
            "uc_id": [
                gerar_uc_id(row["COD_ID"], ano, camada, dist_id)
                for _, row in gdf.iterrows()
            ],
            "import_id": import_id,
            "cod_id": gdf["COD_ID"],
            "distribuidora_id": dist_id,
            "origem": camada,
            "ano": ano,
            "status": "raw",
            "data_conexao": pd.to_datetime(gdf["DAT_CON"], errors="coerce"),
            "cnae": sanitize_cnae(gdf["CNAE"]),
            "grupo_tensao": gdf["GRU_TEN"].apply(sanitize_grupo_tensao),
            "modalidade": gdf["GRU_TAR"].apply(sanitize_modalidade),
            "tipo_sistema": gdf["TIP_SIST"].apply(sanitize_tipo_sistema),
            "situacao": gdf["SIT_ATIV"].apply(sanitize_situacao),
            "classe": gdf["CLAS_SUB"].apply(sanitize_classe),
            "segmento": None,
            "subestacao": sanitize_str(gdf.get("SUB")),
            "municipio_id": sanitize_int(gdf["MUN"]),
            "bairro": sanitize_str(gdf["BRR"]),
            "cep": sanitize_int(gdf["CEP"]),
            "pac": gdf["PAC"].apply(sanitize_pac),
            "pn_con": sanitize_str(gdf["PN_CON"]),
            "descricao": sanitize_str(gdf["DESCR"]),
        })

        duplicados = df_bruto[df_bruto.duplicated(subset=["uc_id"], keep=False)]
        if not duplicados.empty:
            tqdm.write(f" {len(duplicados)} registros duplicados de uc_id detectados e ignorados.")
            df_bruto = df_bruto.drop_duplicates(subset=["uc_id"], keep="first").reset_index(drop=True)

        df_bruto = df_bruto[df_bruto["uc_id"].notnull()].reset_index(drop=True)
        gdf = gdf.loc[df_bruto.index].reset_index(drop=True)

<<<<<<< HEAD
        tqdm.write(" Transformando UCBT para lead_energia_mensal...")
        energia_df = []
        for mes in range(1, 13):
            energia_df.append(pd.DataFrame({
                "uc_id": df_bruto["uc_id"],
                "mes": mes,
                "energia_ponta": None,
                "energia_fora_ponta": None,
                "energia_total": sanitize_numeric(gdf.get(f"ENE_{mes:02d}")),
                "origem": camada
            }))
        df_energia = pd.concat(energia_df).reset_index(drop=True)

        tqdm.write(" Transformando UCBT para lead_demanda_mensal...")
        df_demanda = pd.DataFrame(columns=[
            "lead_bruto_id", "mes", "demanda_ponta", "demanda_fora_ponta", "demanda_total", "demanda_contratada", "origem"
        ])  # vazio pois UCBT não tem colunas de demanda

        tqdm.write(" Transformando UCBT para lead_qualidade_mensal...")
        qualidade_df = []
        for mes in range(1, 13):
            qualidade_df.append(pd.DataFrame({
                "uc_id": df_bruto["uc_id"],
                "mes": mes,
                "dic": sanitize_numeric(gdf.get(f"DIC_{mes:02d}")),
                "fic": sanitize_numeric(gdf.get(f"FIC_{mes:02d}")),
                "sem_rede": sanitize_numeric(gdf.get("SEMRED")),
                "origem": camada
            }))
        df_qualidade = pd.concat(qualidade_df).reset_index(drop=True)
=======
        tqdm.write(" Transformando UCBT para tabelas normalizadas...")
        df_bruto, df_energia, df_qualidade, df_demanda = normalizar_dataframe_para_tabelas(
            gdf, ano, camada, dist_id, import_id,
            campos_energia=campos_energia,
            campos_qualidade=campos_qualidade,
            campos_demanda=campos_demanda
        )
>>>>>>> 56e553dd86508d8dc28552b23dc773f6d22225a1

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                tqdm.write(" Inserindo no banco (lead_bruto)...")
                insert_copy(cur, df_bruto, "lead_bruto", df_bruto.columns.tolist())
            conn.commit()

            df_ids = pd.read_sql("""
                SELECT id AS lead_bruto_id, uc_id
                FROM lead_bruto
                WHERE import_id = %s
            """, conn, params=(import_id,))

        df_energia = df_energia.merge(df_ids, on="uc_id").drop(columns=["uc_id"])
        df_qualidade = df_qualidade.merge(df_ids, on="uc_id").drop(columns=["uc_id"])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                insert_copy(cur, df_energia, "lead_energia_mensal", df_energia.columns.tolist())
                insert_copy(cur, df_qualidade, "lead_qualidade_mensal", df_qualidade.columns.tolist())
            conn.commit()

<<<<<<< HEAD
        registrar_status(
            prefixo, ano, camada, "completed",
            linhas_processadas=len(df_bruto),
            import_id=import_id
        )
=======
        registrar_status(prefixo, ano, camada, "completed")
>>>>>>> 56e553dd86508d8dc28552b23dc773f6d22225a1
        tqdm.write(" Importação UCBT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f" Erro ao importar UCBT: {e}")
<<<<<<< HEAD
        registrar_status(
            prefixo, ano, camada, "failed",
            erro=str(e),
            import_id=import_id
        )
=======
        registrar_status(prefixo, ano, camada, "failed", erro=str(e))
>>>>>>> 56e553dd86508d8dc28552b23dc773f6d22225a1
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

    importar_ucbt(
        gdb_path=args.gdb,
        distribuidora=args.distribuidora,
        ano=args.ano,
        prefixo=args.prefixo,
        modo_debug=args.modo_debug
    )
