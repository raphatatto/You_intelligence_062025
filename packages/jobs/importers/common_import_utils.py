import hashlib
from datetime import datetime
from io import StringIO
from typing import Optional

import pandas as pd
from fiona import listlayers
from tqdm import tqdm

from packages.jobs.utils.sanitize import (
    sanitize_numeric,
    sanitize_cnae,
    sanitize_int,
    sanitize_str,
    sanitize_modalidade,
    sanitize_grupo_tensao,
    sanitize_tipo_sistema,
)


def detectar_layer(gdb_path, prefixo: str) -> Optional[str]:
    """Detecta a layer dentro do GDB com base no prefixo (ex: UCAT, UCMT, UCBT)"""
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith(prefixo.upper())), None)


def gerar_uc_id(cod_id: str, ano: int, camada: str, distribuidora_id: int) -> str:
    """Gera um identificador único para a unidade consumidora"""
    base = f"{cod_id}_{ano}_{camada}_{distribuidora_id}"
    return hashlib.sha256(base.encode()).hexdigest()[:24]


def validar_df_bruto(df_bruto: pd.DataFrame, campos_obrigatorios: list[str]) -> pd.DataFrame:
    """
    Remove registros com campos obrigatórios nulos. Loga os descartados.
    """
    antes = len(df_bruto)
    for campo in campos_obrigatorios:
        df_bruto = df_bruto[df_bruto[campo].notnull()]
    depois = len(df_bruto)
    removidos = antes - depois
    if removidos > 0:
        tqdm.write(f"⚠️ {removidos} registros removidos por campos obrigatórios ausentes: {campos_obrigatorios}")
    return df_bruto


def copy_to_table(conn, df: pd.DataFrame, table: str):
    """Realiza o COPY otimizado para o PostgreSQL"""
    output = StringIO()
    df.to_csv(output, sep=";", index=False, header=False, na_rep="\\N")
    output.seek(0)
    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY {table} FROM STDIN WITH (FORMAT CSV, DELIMITER ';', NULL '\\N')",
            output,
        )
    tqdm.write(f"✅ Inserido em {table}: {len(df)} registros.")


def registrar_status(conn, import_id: str, etapa: str, status: str, erro: Optional[str] = None, linhas: Optional[int] = None):
    """Atualiza status de importação na tabela import_status"""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE import_status
            SET status = %s,
                data_execucao = %s,
                erro = %s,
                linhas_processadas = %s
            WHERE import_id = %s AND etapa = %s
        """,
            (status, datetime.utcnow(), erro, linhas, import_id, etapa),
        )


def normalizar_dataframe_para_tabelas(
    gdf: pd.DataFrame,
    ano: int,
    camada: str,
    distribuidora_id: int,
    import_id: str,
    campos_energia: list,
    campos_qualidade: list,
    campos_demanda: list,
):
    """Transforma o GDF original em quatro DataFrames: lead_bruto, energia, qualidade, demanda"""

    df_bruto = pd.DataFrame({
        "uc_id": [
            gerar_uc_id(row["COD_ID"], ano, camada, distribuidora_id)
            for _, row in gdf.iterrows()
        ],
        "import_id": import_id,
        "cod_id": gdf["COD_ID"],
        "distribuidora_id": distribuidora_id,
        "origem": camada,
        "ano": ano,
        "status": "raw",
        "data_conexao": pd.to_datetime(gdf["DAT_CON"], errors="coerce"),
        "cnae": sanitize_cnae(gdf["CNAE"]),
        "grupo_tensao": gdf["GRU_TEN"].apply(sanitize_grupo_tensao),
        "modalidade": gdf["GRU_TAR"].apply(sanitize_modalidade),
        "tipo_sistema": gdf["TIP_SIST"].apply(sanitize_tipo_sistema),
        "situacao": sanitize_str(gdf.get("SIT_ATIV")),
        "classe": sanitize_str(gdf.get("CLAS_SUB")),
        "segmento": None,
        "subestacao": sanitize_str(gdf.get("CONJ")),
        "municipio_id": sanitize_int(gdf.get("MUN")),
        "bairro": sanitize_str(gdf.get("BRR")),
        "cep": sanitize_str(gdf.get("CEP")),
        "pn_con": sanitize_str(gdf.get("PN_CON")),
        "descricao": sanitize_str(gdf.get("DESCR")),
        "pac": sanitize_numeric(gdf.get("PAC")),
    })

    df_bruto = validar_df_bruto(df_bruto, campos_obrigatorios=["uc_id", "cod_id", "import_id"])

    df_energia = gdf[campos_energia].copy()
    df_energia.columns = ["uc_id", "mes", "energia_ponta", "energia_fora_ponta", "energia_total"]
    df_energia["import_id"] = import_id
    df_energia["origem"] = camada

    df_qualidade = gdf[campos_qualidade].copy()
    df_qualidade.columns = ["uc_id", "mes", "dic", "fic", "semrede"]
    df_qualidade["import_id"] = import_id
    df_qualidade["origem"] = camada

    df_demanda = gdf[campos_demanda].copy()
    df_demanda.columns = ["uc_id", "mes", "demanda_ponta", "fora_ponta", "contratada", "total"]
    df_demanda["import_id"] = import_id
    df_demanda["origem"] = camada

    return df_bruto, df_energia, df_qualidade, df_demanda
