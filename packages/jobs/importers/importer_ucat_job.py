# packages/jobs/importers/importer_ucat_job.py

import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm
from psycopg2.extras import execute_batch
from fiona import listlayers

from packages.database.connection import get_db_cursor
from packages.jobs.utils.rastreio import registrar_status

# Se quiser detectar dinamicamente:
def _detect_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next(l for l in layers if l.upper().startswith("UCAT"))

BATCH_SIZE = 5_000

def _chunkify(df: pd.DataFrame, size: int = BATCH_SIZE):
    records = df.to_dict("records")
    for i in range(0, len(records), size):
        yield records[i : i + size]

def main(
    gdb_path: Path,
    distribuidora: str,
    ano: int,
    prefixo: str,
    camada: str = "UCAT_tab",
    modo_debug: bool = False,
):
    registrar_status(prefixo, ano, camada, "started")
    try:
        # identifica o nome exato da layer
        layer_name = _detect_layer(gdb_path)
        tqdm.write(f"📖 Lendo camada '{layer_name}' do GDB...")
        gdf = gpd.read_file(str(gdb_path), layer=layer_name)
        total = len(gdf)
        tqdm.write(f"   → {total} feições encontradas.")

        # 1) lead_bruto
        df_bruto = pd.DataFrame({
            "cod_id":            gdf["COD_ID"],
            "cod_distribuidora": distribuidora,
            "origem":            "UCAT",
            "ano":               ano,
            "status":            "raw",
            "data_conexao":      pd.to_datetime(gdf.get("DAT_CON", None), errors="coerce"),
            "cnae":              gdf.get("CNAE", None),
            "grupo_tensao":      gdf.get("GRU_TEN", None),
            "modalidade":        gdf.get("GRU_TAR", None),
            "tipo_sistema":      gdf.get("TIP_SIST", None),
            "situacao":          gdf.get("SIT_ATIV", None),
            "classe":            gdf.get("CLAS_SUB", None),
            "segmento":          gdf.get("CONJ", None),
            "subestacao":        None,
            "municipio_ibge":    gdf.get("MUN", None),
            "bairro":            gdf.get("BRR", None),
            "cep":               gdf.get("CEP", None),
            "pac":               gdf.get("PAC", None),
            "pn_con":            gdf.get("PN_CON", None),
            "descricao":         gdf.get("DESCR", "").fillna(""),
        })

        # 2) lead_demanda (média anual a partir de DEM_P_XX e DEM_F_XX)
        cols_p = [f"DEM_P_{i:02d}" for i in range(1, 13)]
        cols_f = [f"DEM_F_{i:02d}" for i in range(1, 13)]
        df_demanda = pd.DataFrame({
            "cod_distribuidora": distribuidora,
            "cod_id":            gdf["COD_ID"],
            "ano":               ano,
            "dem_ponta":         gdf[cols_p].mean(axis=1),
            "dem_fora_ponta":    gdf[cols_f].mean(axis=1),
        })

        # 3) lead_energia — exemplo com ENE_P_XX e ENE_F_XX
        cols_ep = [f"ENE_P_{i:02d}" for i in range(1, 13)]
        cols_ef = [f"ENE_F_{i:02d}" for i in range(1, 13)]
        df_energia = pd.DataFrame({
            "cod_distribuidora": distribuidora,
            "cod_id":            gdf["COD_ID"],
            "ano":               ano,
            "consumo":           gdf[cols_ep + cols_ef].sum(axis=1),
            "potencia":          gdf[cols_ep + cols_ef].max(axis=1),
        })

        # SQL statements
        sql_bruto = """
            INSERT INTO lead_bruto (
                cod_id, cod_distribuidora, origem, ano, status, data_conexao,
                cnae, grupo_tensao, modalidade, tipo_sistema, situacao, classe,
                segmento, subestacao, municipio_ibge, bairro, cep,
                pac, pn_con, descricao
            ) VALUES (
                %(cod_id)s, %(cod_distribuidora)s, %(origem)s, %(ano)s, %(status)s,
                %(data_conexao)s, %(cnae)s, %(grupo_tensao)s, %(modalidade)s,
                %(tipo_sistema)s, %(situacao)s, %(classe)s, %(segmento)s,
                %(subestacao)s, %(municipio_ibge)s, %(bairro)s, %(cep)s,
                %(pac)s, %(pn_con)s, %(descricao)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """
        sql_demanda = """
            INSERT INTO lead_demanda (
                cod_distribuidora, cod_id, ano, dem_ponta, dem_fora_ponta
            ) VALUES (
                %(cod_distribuidora)s, %(cod_id)s, %(ano)s, %(dem_ponta)s, %(dem_fora_ponta)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """
        sql_energia = """
            INSERT INTO lead_energia (
                cod_distribuidora, cod_id, ano, consumo, potencia
            ) VALUES (
                %(cod_distribuidora)s, %(cod_id)s, %(ano)s, %(consumo)s, %(potencia)s
            ) ON CONFLICT (cod_distribuidora, cod_id, ano) DO NOTHING
        """

        # Batch inserts
        with get_db_cursor(commit=True) as cur:
            for batch in tqdm(_chunkify(df_bruto), desc="UCAT_bruto", unit="batch"):
                execute_batch(cur, sql_bruto, batch)
            tqdm.write("✅ lead_bruto inserido")

            for batch in tqdm(_chunkify(df_demanda), desc="UCAT_demanda", unit="batch"):
                execute_batch(cur, sql_demanda, batch)
            tqdm.write("✅ lead_demanda inserido")

            for batch in tqdm(_chunkify(df_energia), desc="UCAT_energia", unit="batch"):
                execute_batch(cur, sql_energia, batch)
            tqdm.write("✅ lead_energia inserido")

        registrar_status(prefixo, ano, camada, "success")

    except Exception as e:
        tqdm.write(f"❌ Erro na importação UCAT: {e}")
        registrar_status(prefixo, ano, camada, f"failed: {e}")
        if modo_debug:
            raise
