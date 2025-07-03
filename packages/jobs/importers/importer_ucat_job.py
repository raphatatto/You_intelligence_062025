import os
import io
import hashlib
import pandas as pd
import geopandas as gpd
from pathlib import Path
from fiona import listlayers
from tqdm import tqdm

from packages.database.connection import get_db_cursor
from packages.jobs.utils.rastreio import registrar_status
from packages.jobs.utils.sanitizadores import sanitize_numeric


def _detect_layer(gdb_path: Path) -> str:
    layers = listlayers(str(gdb_path))
    return next(l for l in layers if l.upper().startswith("UCAT"))


def _to_optional_int(series: pd.Series) -> pd.Series:
    def to_int(x):
        try:
            return int(float(x))
        except:
            return None
    return series.map(to_int)


def gerar_uc_id(row) -> str:
    try:
        base = f"{int(row['cod_distribuidora'])}_{row['cod_id']}_{int(row['ano'])}"
        return hashlib.sha256(base.encode()).hexdigest()
    except Exception as e:
        tqdm.write(f"❌ Erro ao gerar uc_id: {e} | linha: {row.to_dict()}")
        return None


def insert_copy(cur, df, table, columns):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep=r"\N")
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf
    )
    tqdm.write(f"✅ {table} inserido com {len(df)} registros.")


def main(gdb_path: Path, distribuidora: str, ano: int, prefixo: str, camada: str = "UCAT_tab", modo_debug: bool = False):
    registrar_status(prefixo, ano, camada, "started")

    try:
        layer_name = _detect_layer(gdb_path)
        tqdm.write(f"📖 Lendo camada '{layer_name}' do GDB...")
        gdf = gpd.read_file(str(gdb_path), layer=layer_name)
        if len(gdf) == 0:
            registrar_status(prefixo, ano, camada, "no_new_rows")
            return
        tqdm.write(f"   → {len(gdf)} feições encontradas.")

        col_sujas = gdf.columns[gdf.astype(str).apply(lambda col: col.str.contains("106022|YEL", na=False)).any()]
        for col in col_sujas:
            tqdm.write(f"🧼 Removendo coluna suja: {col}")
            gdf.drop(columns=[col], inplace=True)

        def get_series(name):
            return gdf[name] if name in gdf.columns else pd.Series([None] * len(gdf), index=gdf.index)

        tqdm.write("🧱 Construindo DataFrame bruto...")
        s_dist = _to_optional_int(get_series("DIST"))
        s_cnae = _to_optional_int(get_series("CNAE"))
        s_mun = _to_optional_int(get_series("MUN"))
        s_cep = _to_optional_int(get_series("CEP"))
        s_pac = _to_optional_int(get_series("PAC"))
        s_dt_con = pd.to_datetime(get_series("DAT_CON"), errors="coerce")

        df_bruto = pd.DataFrame({
            "cod_id":            gdf["COD_ID"],
            "cod_distribuidora": s_dist,
            "origem":            "UCAT",
            "ano":               ano,
            "status":            "raw",
            "data_conexao":      s_dt_con,
            "cnae":              s_cnae,
            "grupo_tensao":      get_series("GRU_TEN"),
            "modalidade":        get_series("GRU_TAR"),
            "tipo_sistema":      get_series("TIP_SIST"),
            "situacao":          get_series("SIT_ATIV"),
            "classe":            get_series("CLAS_SUB"),
            "segmento":          get_series("CONJ"),
            "subestacao":        get_series("SUB") if "SUB" in gdf.columns else None,
            "municipio_ibge":    s_mun,
            "bairro":            get_series("BRR"),
            "cep":               s_cep,
            "pac":               s_pac,
            "pn_con":            get_series("PN_CON"),
            "descricao":         get_series("DESCR").fillna("")
        })

        df_bruto = df_bruto[df_bruto["cod_id"].notna()].drop_duplicates(subset=["cod_distribuidora", "cod_id", "ano"])
        tqdm.write("🔑 Gerando uc_id...")
        df_bruto["uc_id"] = df_bruto.apply(gerar_uc_id, axis=1)
        df_bruto = df_bruto[df_bruto["uc_id"].notna()].reset_index(drop=True)
        tqdm.write("✅ uc_id gerado com sucesso")

        tqdm.write("📊 Gerando DataFrame de demanda...")
        cols_p = [f"DEM_P_{i:02d}" for i in range(1, 13)]
        cols_f = [f"DEM_F_{i:02d}" for i in range(1, 13)]
        df_demanda = pd.DataFrame({
            "uc_id": df_bruto["uc_id"],
            "dem_ponta": sanitize_numeric(gdf[cols_p]).mean(axis=1),
            "dem_fora_ponta": sanitize_numeric(gdf[cols_f]).mean(axis=1)
        })

        tqdm.write("📈 Gerando DataFrame de energia...")
        cols_ep = [f"ENE_P_{i:02d}" for i in range(1, 13)]
        cols_ef = [f"ENE_F_{i:02d}" for i in range(1, 13)]
        energia = sanitize_numeric(gdf[cols_ep + cols_ef])
        df_energia = pd.DataFrame({
            "uc_id": df_bruto["uc_id"],
            "consumo": energia.sum(axis=1),
            "potencia": energia.max(axis=1)
        })

        # Inserção no banco
        with get_db_cursor(commit=True) as cur:
            tqdm.write("🚀 Enviando para o banco via COPY...")
            insert_copy(cur, df_bruto, "lead_bruto", df_bruto.columns.tolist())
            insert_copy(cur, df_demanda, "lead_demanda", ["uc_id", "dem_ponta", "dem_fora_ponta"])
            insert_copy(cur, df_energia, "lead_energia", ["uc_id", "consumo", "potencia"])

            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (distribuidora, ano)
                DO UPDATE SET camada = EXCLUDED.camada, status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "success"))

        registrar_status(prefixo, ano, camada, "success")
        tqdm.write("🎉 Importação finalizada com sucesso!")

    except Exception as e:
        tqdm.write(f"❌ Erro na importação UCAT: {e}")
        registrar_status(prefixo, ano, camada, f"failed: {e}")
        if modo_debug:
            raise
