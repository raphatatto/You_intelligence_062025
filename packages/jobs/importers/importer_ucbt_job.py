import os
import io
import hashlib
import pandas as pd
import geopandas as gpd
from pathlib import Path
from fiona import listlayers
from dotenv import load_dotenv
from datetime import datetime
from packages.database.connection import get_db_cursor

load_dotenv()

def _to_pg_array(data):
    def fmt(lst):
        return "{" + ",".join(map(str, lst)) + "}" if len(lst) > 0 else r"\N"
    return pd.Series([fmt(row) for row in data])

def hash_endereco(bairro: str, cep: str, municipio: str, distribuidora: str) -> str:
    texto = f"{bairro or ''}-{cep or ''}-{municipio or ''}-{distribuidora or ''}".lower()
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def normalizar_cep(cep: str) -> str:
    if not cep:
        return ""
    return ''.join(filter(str.isdigit, str(cep)))[:8]

def main(gdb_path: Path, distribuidora: str, ano: int, camada: str = "UCBT_tab"):
    if camada not in listlayers(gdb_path):
        print(f"❌ Camada {camada} não encontrada em {gdb_path.name}")
        return

    print(f"📥 Lendo camada '{camada}' do arquivo {gdb_path.name}")
    df = gpd.read_file(gdb_path, layer=camada)

    try:
        col_sujas = df.columns[df.astype(str).apply(lambda col: col.str.contains("106022|YEL", na=False)).any()]
        for col in col_sujas:
            print(f"🧼 Removendo coluna suja: {col}")
            df.drop(columns=[col], inplace=True)

        df["CEP"] = df["CEP"].astype(str).apply(normalizar_cep)
        df["id_interno"] = df.apply(lambda row: hash_endereco(row.get("BRR"), row.get("CEP"), row.get("MUN"), distribuidora), axis=1)

        with get_db_cursor() as cur_check:
            cur_check.execute("SELECT cod_id FROM plead.unidade_consumidora WHERE cod_id = ANY(%s)", (list(df["COD_ID"]),))
            cods_existentes = {row[0] for row in cur_check.fetchall()}
        df = df[~df["COD_ID"].isin(cods_existentes)]

        if df.empty:
            print("⚠️ Nenhum novo registro UCBT para importar.")
            return

        df_lead = df[["id_interno", "CEP", "BRR", "MUN"]].drop_duplicates(subset="id_interno").copy()
        df_lead["id"] = df_lead["id_interno"]
        df_lead["bairro"] = df_lead["BRR"]
        df_lead["cep"] = df_lead["CEP"]
        df_lead["municipio_ibge"] = df_lead["MUN"]
        df_lead["distribuidora"] = distribuidora
        df_lead["status"] = "raw"
        df_lead["ultima_atualizacao"] = datetime.utcnow()
        df_lead = df_lead[["id", "id_interno", "bairro", "cep", "municipio_ibge", "distribuidora", "status", "ultima_atualizacao"]]

        df_uc = pd.DataFrame({
            "id": df["COD_ID"],
            "cod_id": df["COD_ID"],
            "lead_id": df["id_interno"],
            "origem": camada,
            "ano": ano,
            "data_conexao": pd.to_datetime(df.get("DAT_CON"), errors="coerce"),
            "tipo_sistema": df.get("TIP_SIST"),
            "grupo_tensao": df.get("GRU_TEN"),
            "modalidade": df.get("GRU_TAR"),
            "situacao": df.get("SIT_ATIV"),
            "classe": df.get("CLAS_SUB"),
            "segmento": df.get("CONJ"),
            "subestacao": df.get("SUB"),
            "cnae": df.get("CNAE"),
            "descricao": df.get("DESCR"),
            "potencia": df.get("CAR_INST", pd.Series([0]*len(df))).fillna(0).astype(float)
        })

        ene = [c for c in df.columns if c.startswith("ENE_")]
        df_energia = pd.DataFrame({
            "id": df["COD_ID"],
            "uc_id": df["COD_ID"],
            "ene": _to_pg_array(df[ene].fillna(0).astype(int).values) if ene else None,
            "potencia": df.get("CAR_INST", pd.Series([0]*len(df))).fillna(0).astype(float)
        })

        dic = [c for c in df.columns if c.startswith("DIC_")]
        fic = [c for c in df.columns if c.startswith("FIC_")]
        df_qualidade = pd.DataFrame({
            "id": df["COD_ID"],
            "uc_id": df["COD_ID"],
            "dic": _to_pg_array(df[dic].fillna(0).astype(int).values) if dic else None,
            "fic": _to_pg_array(df[fic].fillna(0).astype(int).values) if fic else None
        })

        with get_db_cursor(commit=True) as cur:
            for table, df_data in [
                ("plead.lead", df_lead),
                ("plead.unidade_consumidora", df_uc),
                ("plead.lead_energia", df_energia),
                ("plead.lead_qualidade", df_qualidade)
            ]:
                if df_data.empty: continue
                buf = io.StringIO()
                df_data.to_csv(buf, index=False, header=False, na_rep=r"\N")
                buf.seek(0)
                cur.copy_expert(
                    f"COPY {table} ({','.join(df_data.columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
                print(f"📤 Inseridos {len(df_data)} registros em {table}")

            cur.execute("""
                INSERT INTO plead.import_status (distribuidora, ano, camada, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (distribuidora, ano, camada)
                DO UPDATE SET status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "success"))

        print("✅ UCBT importado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao importar UCBT: {e}")
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO plead.import_status (distribuidora, ano, camada, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (distribuidora, ano, camada)
                DO UPDATE SET status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "failed"))
