#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import io
from datetime import datetime
from typing import Sequence, Any
import geopandas as gpd
import pandas as pd
from fiona import listlayers

from packages.database.connection import get_db_cursor


def _to_pg_array(data: Sequence[Sequence[Any]] | pd.Series) -> list[str] | pd.Series:
    def fmt(lst): return "{" + ",".join(map(str, lst)) + "}" if len(lst) > 0 else r"\N"
    return data.apply(fmt) if isinstance(data, pd.Series) else [fmt(lst) for lst in data]


def _copy_df(df: pd.DataFrame, table: str, cur) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, na_rep=r"\N")
    buf.seek(0)
    cur.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)


def importar_ucat(gdb: Path, distribuidora: str, ano: int):
    layer = "UCAT_tab"
    if layer not in listlayers(gdb):
        print(f"⚠️  Camada {layer} não encontrada em {gdb.name}. Pulando.")
        return

    print(f"📥 Lendo ‘{layer}’ em {gdb.name}…")
    df = gpd.read_file(gdb, layer=layer)

    # 🔧 Forçando a data para 2023-01-01
    df["data_conexao"] = pd.to_datetime("2023-01-01").date()

    dem_p = [c for c in df.columns if c.startswith("DEM_P_")]
    dem_f = [c for c in df.columns if c.startswith("DEM_F_")]
    ene_p = [c for c in df.columns if c.startswith("ENE_P_")]
    ene_f = [c for c in df.columns if c.startswith("ENE_F_")]
    dic = [c for c in df.columns if c.startswith("DIC_")]
    fic = [c for c in df.columns if c.startswith("FIC_")]

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
    "data_conexao": pd.Series([pd.Timestamp("2023-01-01")] * len(df)),
    "classe": df.get("CLAS_SUB"),
    "segmento": df.get("CONJ"),
    "subestacao": df.get("SUB"),
    "municipio_ibge": df.get("MUN"),
    "bairro": df.get("BRR"),
    "cep": df.get("CEP"),
    "pac": df.get("PAC"),
    "pn_con": df.get("PN_CON"),
})


    df_demanda = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "dem_ponta": _to_pg_array(df[dem_p].fillna(0).values),
        "dem_fora_ponta": _to_pg_array(df[dem_f].fillna(0).values),
    })

    df_energia = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "ene": _to_pg_array((df[ene_p].fillna(0).values + df[ene_f].fillna(0).values)),
        "potencia": df["DEM_CONT"].fillna(0).astype(float),
    })

    df_q = pd.DataFrame({
        "id": df["COD_ID"],
        "lead_id": df["COD_ID"],
        "dic": _to_pg_array(df[dic].fillna(0).values),
        "fic": _to_pg_array(df[fic].fillna(0).values),
    })

    with get_db_cursor(commit=True) as cur:
        _copy_df(df_bruto, "lead_bruto", cur)
        _copy_df(df_demanda, "lead_demanda", cur)
        _copy_df(df_energia, "lead_energia", cur)
        _copy_df(df_q, "lead_qualidade", cur)

    print(f"✅ UCAT {distribuidora.upper()}-{ano}: {len(df)} registros inseridos.")
