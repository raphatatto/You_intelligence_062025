import geopandas as gpd
import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Conexão com o banco
conn_str = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
engine = create_engine(conn_str)

# Caminho do GDB e nome da camada
GDB_PATH = "data/downloads/SEU_ARQUIVO.gdb"  # ajuste conforme necessário
LAYER_NAME = "PONNOT"

# Leitura com GeoPandas
gdf = gpd.read_file(GDB_PATH, layer=LAYER_NAME)

# Extrai coordenadas x, y
gdf["lat"] = gdf.geometry.y
gdf["lng"] = gdf.geometry.x

# Limpa e deixa só os que têm coordenada válida
gdf = gdf[["COD_ID", "lat", "lng"]].dropna()

# Cria coordenada como JSON
gdf["coordenadas"] = gdf.apply(lambda row: {"lat": row["lat"], "lng": row["lng"]}, axis=1)

# Conecta e atualiza no banco
with engine.begin() as conn:
    for _, row in gdf.iterrows():
        conn.execute("""
            UPDATE plead.lead_bruto
            SET coordenadas = %s
            WHERE cod_id = %s
              AND (coordenadas IS NULL OR coordenadas = '{}')
        """, (row["coordenadas"], row["COD_ID"]))
