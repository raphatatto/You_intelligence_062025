import os
import io
import hashlib
import pandas as pd
import geopandas as gpd
from pathlib import Path
from fiona import listlayers
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Conexão assíncrona com o banco de dados
DB_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
)
engine = create_async_engine(DB_URL, echo=False)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Utilitário para arrays PostgreSQL
def _to_pg_array(data):
    def fmt(lst): return "{" + ",".join(map(str, lst)) + "}" if len(lst) > 0 else r"\N"
    return pd.Series([fmt(row) for row in data])

# Função para salvar status no banco (ajustada ao seu schema)
async def salvar_status(db, distribuidora, ano, camada, status):
    await db.execute(text("""
        INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
        VALUES (:dist, :ano, :camada, :status, now())
    """), {
        "dist": distribuidora,
        "ano": ano,
        "camada": camada,
        "status": status
    })
    await db.commit()

# Função principal parametrizada
async def main(gdb_path: Path, distribuidora: str, ano: int, camada: str):
    if camada not in listlayers(gdb_path):
        print(f"❌ Camada {camada} não encontrada em {gdb_path.name}")
        return

    print(f"📥 Lendo camada '{camada}' do arquivo {gdb_path.name}")
    df = gpd.read_file(gdb_path, layer=camada)

    async with Session() as db:
        try:
            df["data_conexao"] = pd.to_datetime("2023-01-01").date()
            df["distribuidora"] = distribuidora
            df["origem"] = camada
            df["status"] = "raw"

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
                "distribuidora": df["distribuidora"],
                "origem": df["origem"],
                "status": df["status"],
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

            df_qualidade = pd.DataFrame({
                "id": df["COD_ID"],
                "lead_id": df["COD_ID"],
                "dic": _to_pg_array(df[dic].fillna(0).values),
                "fic": _to_pg_array(df[fic].fillna(0).values),
            })

            for name, df_final in {
                "lead_bruto": df_bruto,
                "lead_demanda": df_demanda,
                "lead_energia": df_energia,
                "lead_qualidade": df_qualidade,
            }.items():
                print(f"📤 Enviando {len(df_final)} registros para {name}")
                buf = io.StringIO()
                df_final.to_csv(buf, index=False, header=False, na_rep=r"\N")
                buf.seek(0)
                await db.copy_expert(f"COPY {name} FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)

            await salvar_status(db, distribuidora, ano, camada, "success")
            print("✅ UCAT importado com sucesso!")

        except Exception as e:
            print("❌ Erro ao importar UCAT:", str(e))
            await salvar_status(db, distribuidora, ano, camada, "failed")
