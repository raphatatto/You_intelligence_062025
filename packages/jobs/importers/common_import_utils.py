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
    sanitize_situacao,
    sanitize_classe,
)


def detectar_layer(gdb_path, prefixo: str) -> Optional[str]:
    layers = listlayers(str(gdb_path))
    return next((l for l in layers if l.upper().startswith(prefixo.upper())), None)


def gerar_uc_id(cod_id: str, ano: int, camada: str, distribuidora_id: int) -> str:
    base = f"{cod_id}_{ano}_{camada}_{distribuidora_id}"
    return hashlib.sha256(base.encode()).hexdigest()[:24]


def validar_df_bruto(df_bruto: pd.DataFrame, campos_obrigatorios: list[str]) -> pd.DataFrame:
    antes = len(df_bruto)
    for campo in campos_obrigatorios:
        df_bruto = df_bruto[df_bruto[campo].notnull()]
    depois = len(df_bruto)
    removidos = antes - depois
    if removidos > 0:
        tqdm.write(f" {removidos} registros removidos por campos obrigatórios ausentes: {campos_obrigatorios}")
    return df_bruto


def copy_to_table(conn, df: pd.DataFrame, table: str):
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND column_default IS NULL
            ORDER BY ordinal_position
        """, (table,))
        colunas_ordenadas = [row[0] for row in cur.fetchall()]

    df = df.reindex(columns=colunas_ordenadas)

    output = StringIO()
    df.to_csv(output, sep=";", index=False, header=False, na_rep="\\N")
    output.seek(0)

    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY {table} ({', '.join(colunas_ordenadas)}) FROM STDIN WITH (FORMAT CSV, DELIMITER ';', NULL '\\N')",
            output,
        )
    tqdm.write(f" Inserido em {table}: {len(df)} registros.")


def extrair_colunas_validas(campos: list[list]) -> list[str]:
    colunas = set()
    for linha in campos:
        for item in linha:
            if item is not None and isinstance(item, str):
                colunas.add(item)
    return list(colunas)


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
    if "geometry" in gdf.columns:
        gdf = gdf.drop(columns="geometry")

    df_bruto = pd.DataFrame({
    "uc_id": [gerar_uc_id(row["COD_ID"], ano, camada, distribuidora_id) for _, row in gdf.iterrows()],
    "import_id": import_id,
    "cod_id": gdf["COD_ID"],
    "distribuidora_id": distribuidora_id,
    "origem": camada,
    "ano": ano,
    "status": "raw",
    "data_conexao": pd.to_datetime(gdf["DAT_CON"], errors="coerce"),
    "cnae": sanitize_cnae(gdf.get("CNAE")),
    "grupo_tensao": gdf.get("GRU_TEN").apply(sanitize_grupo_tensao),
    "modalidade": gdf.get("GRU_TAR").apply(sanitize_modalidade),
    "tipo_sistema": gdf.get("TIP_SIST").apply(sanitize_tipo_sistema),
    "situacao": gdf.get("SIT_ATIV").apply(sanitize_situacao),
    "classe": gdf.get("CLAS_SUB").apply(sanitize_classe),
    "segmento": None,
    "subestacao": sanitize_str(gdf.get("CONJ")),
    "municipio_id": sanitize_int(gdf.get("MUN")),
    "bairro": sanitize_str(gdf.get("BRR")),
    "cep": sanitize_str(gdf.get("CEP")),
    "pn_con": sanitize_str(gdf.get("PN_CON")),
    "descricao": sanitize_str(gdf.get("DESCR")),
    "pac": sanitize_numeric(gdf.get("PAC")),
    "latitude": None,
    "longitude": None,
    "created_at": datetime.utcnow(),
})


    df_bruto = validar_df_bruto(df_bruto, campos_obrigatorios=["uc_id", "cod_id", "import_id"])

    cols_energia = extrair_colunas_validas(campos_energia)
    cols_qualidade = extrair_colunas_validas(campos_qualidade)
    cols_demanda = extrair_colunas_validas(campos_demanda)

    # Energia
    energia_rows = []
    for linha in campos_energia:
        col_uc, mes, col_ponta, col_fora, col_total = linha
        for idx, row in gdf.iterrows():
            energia_rows.append({
                "uc_id": gerar_uc_id(row[col_uc], ano, camada, distribuidora_id),
                "mes": mes,
                "energia_ponta": row.get(col_ponta),
                "energia_fora_ponta": row.get(col_fora),
                "energia_total": row.get(col_total),
                "import_id": import_id,
                "origem": camada,
            })
    df_energia = pd.DataFrame(energia_rows)

    # Qualidade
    df_semred = sanitize_numeric(gdf.get("SEMRED")) if "SEMRED" in gdf.columns else pd.Series([None] * len(gdf))
    qualidade_rows = []
    for linha in campos_qualidade:
        if len(linha) < 4:
            continue
        col_uc, mes, col_dic, col_fic, *_ = linha
        for idx, row in gdf.iterrows():
            qualidade_rows.append({
                "uc_id": gerar_uc_id(row[col_uc], ano, camada, distribuidora_id),
                "mes": mes,
                "dic": row.get(col_dic),
                "fic": row.get(col_fic),
                "sem_rede": df_semred.iloc[idx] if idx < len(df_semred) else None,
                "import_id": import_id,
                "origem": camada,
            })
    df_qualidade = pd.DataFrame(qualidade_rows)

    # Demanda
    demanda_rows = []
    for linha in campos_demanda:
        col_uc, mes, col_ponta, col_fora, col_cont, col_total = linha
        for idx, row in gdf.iterrows():
            demanda_rows.append({
                "uc_id": gerar_uc_id(row[col_uc], ano, camada, distribuidora_id),
                "mes": mes,
                "demanda_ponta": row.get(col_ponta),
                "fora_ponta": row.get(col_fora),
                "contratada": row.get(col_cont),
                "total": row.get(col_total),
                "import_id": import_id,
                "origem": camada,
            })
    df_demanda = pd.DataFrame(demanda_rows)

    return df_bruto, df_energia, df_qualidade, df_demanda
