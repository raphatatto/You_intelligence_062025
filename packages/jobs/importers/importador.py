import geopandas as gpd
from pathlib import Path
import warnings
import json
import psycopg2
from datetime import datetime

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────
DISTRIBUIDORA = "enel_rj"
ANO = "2023"
CAMADA = "UCMT_tab"
DOWNLOAD_FOLDER = Path("data/downloads")
DB_CONFIG = {
    "host": "localhost",
    "dbname": "youon",
    "user": "postgres",
    "password": "your_password_here"
}

# ─── CONEXÃO COM BANCO ───────────────────────────────────────
def salvar_status_importacao(distribuidora, ano, status):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO import_status (distribuidora, ano, status, data_execucao)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (distribuidora, ano)
            DO UPDATE SET status = EXCLUDED.status, data_execucao = EXCLUDED.data_execucao
        """, (distribuidora, ano, status, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        print(f"🧾 Status salvo: {distribuidora} {ano} → {status}")
    except Exception as e:
        print(f"❌ Erro ao salvar status no banco: {e}")

# ─── ENCONTRAR A GDB ────────────────────────────────────────────
gdb_path = None
for zip_file in DOWNLOAD_FOLDER.glob("*.zip"):
    if DISTRIBUIDORA in zip_file.name.lower() and ANO in zip_file.name:
        extraido = DOWNLOAD_FOLDER / zip_file.stem.replace(".gdb", "")
        gdbs = list(extraido.glob("*.gdb"))
        if gdbs:
            gdb_path = gdbs[0]
        break

if not gdb_path:
    raise FileNotFoundError("❌ GDB não encontrada para essa distribuidora.")

# ─── LER A CAMADA UCMT ──────────────────────────────────────────
print(f"🔍 Lendo camada: {CAMADA} de {gdb_path.name}")
df = gpd.read_file(gdb_path, layer=CAMADA)

# ─── VERIFICAR GEOMETRIA ───────────────────────────────────────
tem_geometry = "geometry" in df.columns

if tem_geometry:
    df = gpd.GeoDataFrame(df, geometry="geometry")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df["lon"] = df.geometry.centroid.copy().x
        df["lat"] = df.geometry.centroid.copy().y
else:
    df["lat"] = None
    df["lon"] = None
    print("⚠️  Camada não possui geometria. Colunas de coordenadas preenchidas como None.")

# ─── VISUALIZAR AMOSTRA COMPLETA ───────────────────────────────
print("\n🧪 Amostra completa de UCMT_tab (10 primeiros registros):")
print(df.head(10).T)  # T = transposto para melhor visualização

# ─── SALVAR STATUS COMO SUCCESS ────────────────────────────────
salvar_status_importacao(DISTRIBUIDORA, ANO, "success")
