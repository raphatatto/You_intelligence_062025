# packages/jobs/importers/importer_ucbt_job.py

import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm
from psycopg2.extras import execute_batch
from fiona import listlayers

from packages.database.connection import get_db_cursor
from packages.jobs.utils.rastreio import registrar_status
from packages.jobs.utils.sanitizadores import sanitize_numeric

BATCH_SIZE = 10_000

def _detect_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next(l for l in layers if l.upper().startswith("UCBT"))

def _chunkify(df: pd.DataFrame, size: int = BATCH_SIZE):
    records = df.to_dict("records")
    for i in range(0, len(records), size):
        yield records[i : i + size]

def _to_optional_int(series: pd.Series) -> pd.Series:
    def to_int(x):
        try:
            return int(float(x))
        except:
            return None
    return series.map(to_int)

def main(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, camada: str="UCBT_tab", modo_debug: bool=False):
    registrar_status(prefixo, ano, camada, "started")
    try:
        layer_name = _detect_layer(gdb_path)
        tqdm.write(f"📖 Lendo camada '{layer_name}' do GDB...")
        gdf = gpd.read_file(str(gdb_path), layer=layer_name)
        total = len(gdf)
        tqdm.write(f"   → {total} feições encontradas.")
        if total == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return

        col_sujas = gdf.columns[
            gdf.astype(str)
               .apply(lambda col: col.str.contains("106022|YEL", na=False))
               .any()
        ]
        for col in col_sujas:
            tqdm.write(f"🧼 Removendo coluna suja: {col}")
            gdf.drop(columns=[col], inplace=True)

        def get_series(name):
            return gdf[name] if name in gdf.columns else pd.Series([None]*len(gdf), index=gdf.index)

        s_dist = _to_optional_int(get_series("DIST"))
        s_cnae = _to_optional_int(get_series("CNAE"))
        s_mun = _to_optional_int(get_series("MUN"))
        s_cep = _to_optional_int(get_series("CEP"))
        s_pac = _to_optional_int(get_series("PAC"))

        df_bruto = pd.DataFrame({
            "cod_id":            gdf["COD_ID"],
            "cod_distribuidora": s_dist,
            "origem":            "UCBT",
            "ano":               ano,
            "status":            "raw",
            "data_conexao":      pd.to_datetime(get_series("DAT_CON"), errors="coerce"),
            "cnae":              s_cnae,
            "grupo_tensao":      get_series("GRU_TEN"),
            "modalidade":        get_series("GRU_TAR"),
            "tipo_sistema":      get_series("TIP_SIST"),
            "situacao":          get_series("SIT_ATIV"),
            "classe":            get_series("CLAS_SUB"),
            "segmento":          get_series("CONJ"),
            "subestacao":        None,
            "municipio_ibge":    s_mun,
            "bairro":            get_series("BRR"),
            "cep":               s_cep,
            "pac":               s_pac,
            "pn_con":            get_series("PN_CON"),
            "descricao":         get_series("DESCR").fillna(""),
        })

        valid = df_bruto["cnae"].notna()
        df_bruto = df_bruto[valid].reset_index(drop=True)

        cols_dic = [f"DIC_{i:02d}" for i in range(1,13)]
        cols_ene = [f"ENE_{i:02d}" for i in range(1,13)]

        dic_df = gdf.loc[valid, cols_dic]
        ene_df = gdf.loc[valid, cols_ene]

        df_demanda = pd.DataFrame({
            "cod_distribuidora": df_bruto["cod_distribuidora"],
            "cod_id":            df_bruto["cod_id"],
            "ano":               ano,
            "dem_ponta":         sanitize_numeric(dic_df).mean(axis=1),
            "dem_fora_ponta":    sanitize_numeric(dic_df).mean(axis=1),
        })

        df_energia = pd.DataFrame({
            "cod_distribuidora": df_bruto["cod_distribuidora"],
            "cod_id":            df_bruto["cod_id"],
            "ano":               ano,
            "consumo":           sanitize_numeric(ene_df).sum(axis=1),
            "potencia":          sanitize_numeric(ene_df).max(axis=1),
        })

        sql_bruto = """
            INSERT INTO lead_bruto (
              cod_id, cod_distribuidora, origem, ano, status, data_conexao,
              cnae, grupo_tensao, modalidade, tipo_sistema, situacao, classe,
              segmento, subestacao, municipio_ibge, bairro, cep,
              pac, pn_con, descricao
            ) VALUES (
              %(cod_id)s, %(cod_distribuidora)s, %(origem)s, %(ano)s,
              %(status)s, %(data_conexao)s, %(cnae)s, %(grupo_tensao)s,
              %(modalidade)s, %(tipo_sistema)s, %(situacao)s, %(classe)s,
              %(segmento)s, %(subestacao)s, %(municipio_ibge)s, %(bairro)s,
              %(cep)s, %(pac)s, %(pn_con)s, %(descricao)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """
        sql_demanda = """
            INSERT INTO lead_demanda (
              cod_distribuidora, cod_id, ano, dem_ponta, dem_fora_ponta
            ) VALUES (
              %(cod_distribuidora)s, %(cod_id)s, %(ano)s,
              %(dem_ponta)s, %(dem_fora_ponta)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """
        sql_energia = """
            INSERT INTO lead_energia (
              cod_distribuidora, cod_id, ano, consumo, potencia
            ) VALUES (
              %(cod_distribuidora)s, %(cod_id)s, %(ano)s,
              %(consumo)s, %(potencia)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """

        with get_db_cursor(commit=True) as cur:
            for batch in tqdm(_chunkify(df_bruto), desc="UCBT_bruto", unit="batch"):
                execute_batch(cur, sql_bruto, batch)
            tqdm.write("✅ lead_bruto inserido")

            for batch in tqdm(_chunkify(df_demanda), desc="UCBT_demanda", unit="batch"):
                execute_batch(cur, sql_demanda, batch)
            tqdm.write("✅ lead_demanda inserido")

            for batch in tqdm(_chunkify(df_energia), desc="UCBT_energia", unit="batch"):
                execute_batch(cur, sql_energia, batch)
            tqdm.write("✅ lead_energia inserido")

        registrar_status(prefixo, ano, camada, "success")

    except Exception as e:
        tqdm.write(f"❌ Erro na importação UCBT: {e}")
        registrar_status(prefixo, ano, camada, f"failed: {e}")
        if modo_debug: raise
