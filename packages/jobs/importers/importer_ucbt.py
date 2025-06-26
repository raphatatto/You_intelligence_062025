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

def importar_ucbt(gdb: Path, distribuidora: str, ano: int):
    layer = "UCBT_tab"
    if layer not in listlayers(gdb):
        print(f"⚠️  Camada {layer} não encontrada em {gdb.name}. Pulando.")
        return

    print(f"📥 Lendo camada '{layer}' de {gdb.name}...")
    df = gpd.read_file(gdb, layer=layer)
    df["data_conexao"] = df.get("DAT_CON", pd.Series()).apply(_coerce_date).fillna(pd.NaT)

    ene_cols = [col for col in df.columns if col.startswith("ENE_")]
    dic_cols = [col for col in df.columns if col.startswith("DIC_")]
    fic_cols = [col for col in df.columns if col.startswith("FIC_")]

    df_bruto = pd.DataFrame({
        "id": df["COD_ID"],
        "id_interno": df["COD_ID"],
        "cnae": df.get("CNAE"),
        "grupo_tensao": df.get("GRU_TEN"),
        "modalidade": df.get("GRU_TAR"),
        "tipo_sistema": df.get("TIP_SIST"),
        "situacao": df.get("SIT_ATIV"),
        "distribuidora": distribuidora,
        "origem": layer.lower(),
        "status": "raw",
        "data_conexao": df["data_conexao"],
        "classe": df.get("CLAS_SUB"),
        "segmento": df.get("CONJ"),
        "subestacao": df.get("SUB"),
        "municipio_ibge": df.get("MUN"),
        "bairro": df.get("BRR"),
        "cep": df.get("CEP"),
        "pac": df.get("PAC"),
        "pn_con": df.get("PN_CON"),
    })

    df_ene = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "ene": _to_pg_array(df[ene_cols].fillna(0).values),
        "potencia": df.get("CAR_INST", pd.Series([0] * len(df))).fillna(0).astype(float),
    })

    df_q = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "dic": _to_pg_array(df[dic_cols].fillna(0).values),
        "fic": _to_pg_array(df[fic_cols].fillna(0).values),
    })

    with get_db_cursor(commit=True) as cur:
        _copy_df(df_bruto, "lead_bruto", cur)
        _copy_df(df_ene, "lead_energia", cur)
        _copy_df(df_q, "lead_qualidade", cur)

    print(f"✅ UCBT {distribuidora.upper()} {ano}: {len(df)} registros inseridos!")
