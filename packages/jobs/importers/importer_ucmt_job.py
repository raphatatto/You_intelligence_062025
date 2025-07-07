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
from packages.jobs.utils.sanitize import sanitize_numeric


REQUIRED_COLUMNS = [
    "COD_ID", "DIST", "CNAE", "DAT_CON", "PAC", "GRU_TEN", "GRU_TAR", "TIP_SIST",
    "SIT_ATIV", "CLAS_SUB", "CONJ", "MUN", "BRR", "CEP", "PN_CON", "DESCR"
]


def detectar_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith("UCMT")), None)


def gerar_uc_id(import_id: str, cod_id: str, cod_distribuidora: int) -> str:
    base = f"{import_id}_{cod_distribuidora}_{cod_id}"
    return hashlib.sha256(base.encode()).hexdigest()


def insert_copy(cur, df: pd.DataFrame, table: str, columns: list[str]):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
    tqdm.write(f"✅ Inserido em {table}: {len(df)} registros.")


def importar_ucmt(
    gdb_path: Path,
    distribuidora: str,
    ano: int,
    prefixo: str,
    modo_debug: bool = False
):
    camada = "UCMT"
    registrar_status(prefixo, ano, camada, "started")
    import_id = gerar_import_id(prefixo, ano, camada)

    try:
        layer = detectar_layer(gdb_path)
        if not layer:
            raise Exception("Camada UCMT não encontrada no GDB.")

        tqdm.write(f"📖 Lendo camada '{layer}'...")
        gdf = gpd.read_file(str(gdb_path), layer=layer)

        if len(gdf) == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return

        # Remoção de colunas sujas
        sujas = gdf.columns[gdf.astype(str).apply(lambda col: col.str.contains("106022|YEL", na=False)).any()]
        gdf.drop(columns=sujas, inplace=True)

        # Validação de campos obrigatórios
        faltantes = [col for col in REQUIRED_COLUMNS if col not in gdf.columns]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {faltantes}")

        tqdm.write("🧱 Transformando UCMT para lead_bruto...")
        df_bruto = pd.DataFrame({
            "uc_id": [gerar_uc_id(import_id, row["COD_ID"], int(row["DIST"])) for _, row in gdf.iterrows()],
            "import_id": import_id,
            "cod_id": gdf["COD_ID"],
            "distribuidora_id": gdf["DIST"].astype("Int64"),
            "origem": "UCMT",
            "ano": ano,
            "status": "raw",
            "data_conexao": pd.to_datetime(gdf["DAT_CON"], errors="coerce"),
            "cnae": gdf["CNAE"].astype("Int64"),
            "grupo_tensao": gdf["GRU_TEN"],
            "modalidade": gdf["GRU_TAR"],
            "tipo_sistema": gdf["TIP_SIST"],
            "situacao": gdf["SIT_ATIV"],
            "classe": gdf["CLAS_SUB"],
            "segmento": gdf["CONJ"],
            "subestacao": None,
            "municipio_id": gdf["MUN"].astype("Int64"),
            "bairro": gdf["BRR"],
            "cep": gdf["CEP"].astype("Int64"),
            "pac": gdf["PAC"].astype("Int64"),
            "pn_con": gdf["PN_CON"],
            "descricao": gdf["DESCR"].fillna(""),
        })

        tqdm.write("📈 Transformando UCMT para lead_energia_mensal...")
        energia_df = []
        for mes in range(1, 13):
            energia_df.append(pd.DataFrame({
                "uc_id": df_bruto["uc_id"],
                "mes": mes,
                "energia_total": sanitize_numeric(gdf[f"ENE_{mes:02d}"]),
                "origem": "UCMT"
            }))
        df_energia = pd.concat(energia_df).reset_index(drop=True)

        tqdm.write("📊 Transformando UCMT para lead_demanda_mensal...")
        demanda_df = []
        for mes in range(1, 13):
            demanda_df.append(pd.DataFrame({
                "uc_id": df_bruto["uc_id"],
                "mes": mes,
                "dem_ponta": sanitize_numeric(gdf[f"DEM_{mes:02d}"]),
                "dem_fora_ponta": sanitize_numeric(gdf[f"DEM_{mes:02d}"]),
                "origem": "UCMT"
            }))
        df_demanda = pd.concat(demanda_df).reset_index(drop=True)

        tqdm.write("📉 Transformando UCMT para lead_qualidade_mensal...")
        qualidade_df = []
        for mes in range(1, 13):
            qualidade_df.append(pd.DataFrame({
                "uc_id": df_bruto["uc_id"],
                "mes": mes,
                "dic": sanitize_numeric(gdf.get(f"DIC_{mes:02d}")),
                "fic": sanitize_numeric(gdf.get(f"FIC_{mes:02d}")),
                "origem": "UCMT"
            }))
        df_qualidade = pd.concat(qualidade_df).reset_index(drop=True)

        # Inserção no banco
        conn = get_db_connection()
        with conn.cursor() as cur:
            tqdm.write("🚀 Inserindo no banco...")
            insert_copy(cur, df_bruto, "lead_bruto", df_bruto.columns.tolist())
            insert_copy(cur, df_energia, "lead_energia_mensal", df_energia.columns.tolist())
            insert_copy(cur, df_demanda, "lead_demanda_mensal", df_demanda.columns.tolist())
            insert_copy(cur, df_qualidade, "lead_qualidade_mensal", df_qualidade.columns.tolist())
        conn.commit()

        registrar_status(prefixo, ano, camada, "success")
        tqdm.write("🎉 Importação UCMT finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f"❌ Erro ao importar UCMT: {e}")
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

    importar_ucmt(
        gdb_path=args.gdb,
        distribuidora=args.distribuidora,
        ano=args.ano,
        prefixo=args.prefixo,
        modo_debug=args.modo_debug
    )
