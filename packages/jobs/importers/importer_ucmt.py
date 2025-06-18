#!/usr/bin/env python3
import io
from pathlib import Path
from datetime import datetime

import geopandas as gpd
import pandas as pd
from fiona import listlayers

from packages.database.connection import get_db_cursor


def _coerce_date(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.upper() in {"YEL", "N/A", "NULO", "NULL", "SEM DADO", ""}:
        return None
    try:
        return pd.to_datetime(s, dayfirst=True, errors="coerce").date()
    except Exception:
        return None


def _to_pg_array(data):
    def fmt(lst):
        return "{" + ",".join(map(str, lst)) + "}" if len(lst) > 0 else r"\N"
    if isinstance(data, pd.Series):
        return data.apply(fmt)
    return [fmt(lst) for lst in data]


def _copy_df(df, table, cur):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)
    cur.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)


def importar_ucmt(gdb: Path, distribuidora: str, ano: int):
    layer = "UCMT_tab"
    if layer not in listlayers(gdb):
        print(f"⚠️  Camada {layer} não encontrada em {gdb.name}. Pulando.")
        return

    print(f"📥 Lendo camada '{layer}' de {gdb.name}...")
    df = gpd.read_file(gdb, layer=layer)
    df["data_conexao"] = df["DAT_CON"].apply(_coerce_date).fillna(pd.NaT)

    dem_p = [col for col in df.columns if col.startswith("DEM_P_")]
    dem_f = [col for col in df.columns if col.startswith("DEM_F_")]
    ene_p = [col for col in df.columns if col.startswith("ENE_P_")]
    ene_f = [col for col in df.columns if col.startswith("ENE_F_")]
    dic_cols = [col for col in df.columns if col.startswith("DIC_")]
    fic_cols = [col for col in df.columns if col.startswith("FIC_")]

    df_bruto = pd.DataFrame({
        "id": df["COD_ID"],
        "id_interno": df["COD_ID"],
        "cnae": df["CNAE"],
        "grupo_tensao": df["GRU_TEN"],
        "modalidade": df["GRU_TAR"],
        "tipo_sistema": df["TIP_SIST"],
        "situacao": df["SIT_ATIV"],
        "distribuidora": distribuidora,
        "origem": layer.lower(),
        "status": "raw",
        "data_conexao": df["data_conexao"],
        "classe": df["CLAS_SUB"],
        "segmento": df["CONJ"],
        "subestacao": df["SUB"],
        "municipio_ibge": df["MUN"],
        "bairro": df["BRR"],
        "cep": df["CEP"],
        "pac": df["PAC"],
        "pn_con": df["PN_CON"],
    })

    df_dem = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "dem_ponta": _to_pg_array(df[dem_p].fillna(0).values),
        "dem_fora_ponta": _to_pg_array(df[dem_f].fillna(0).values),
    })

    df_ene = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "ene": _to_pg_array((df[ene_p].fillna(0).values + df[ene_f].fillna(0).values)),
        "potencia": df["DEM_CONT"].fillna(0).astype(float),
    })

    df_q = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "dic": _to_pg_array(df[dic_cols].fillna(0).values),
        "fic": _to_pg_array(df[fic_cols].fillna(0).values),
    })

    with get_db_cursor(commit=True) as cur:
        _copy_df(df_bruto, "lead_bruto", cur)
        _copy_df(df_dem, "lead_demanda", cur)
        _copy_df(df_ene, "lead_energia", cur)
        _copy_df(df_q, "lead_qualidade", cur)

    print(f"✅ UCMT {distribuidora.upper()} {ano}: {len(df)} registros inseridos!")
