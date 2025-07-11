import geopandas as gpd
from pathlib import Path
import fiona
import zipfile
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── CONFIGURAÇÃO ───────────────────────────────────────────────
DISTRIBUIDORA = "enel_rj"
ANO = "2023"
CAMADAS_ALVO = ["UCAT_tab", "UCMT_tab", "UCBT_tab","PONNOT"]
DOWNLOAD_FOLDER = Path("data/downloads")

# ─── ENCONTRAR O ZIP E A PASTA EXTRAÍDA ─────────────────────────

# Encontra o .zip correspondente
ZIP_PATH = None
for file in DOWNLOAD_FOLDER.glob("*.zip"):
    if DISTRIBUIDORA in file.name.lower() and ANO in file.name:
        ZIP_PATH = file
        break

if not ZIP_PATH:
    raise FileNotFoundError("❌ Arquivo ZIP da distribuidora não encontrado.")

# Pasta de extração
NOME_EXTRAIDO = ZIP_PATH.stem.replace(".gdb", "")
EXTRACT_FOLDER = DOWNLOAD_FOLDER / NOME_EXTRAIDO
EXTRACT_FOLDER.mkdir(parents=True, exist_ok=True)

# Extrai se ainda não estiver extraído
if not any(EXTRACT_FOLDER.glob("*.gdb")):
    print("📂 Extraindo ZIP...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_FOLDER)
    print("✅ Arquivos extraídos para:", EXTRACT_FOLDER)

# ─── LOCALIZA GDB ───────────────────────────────────────────────
gdbs = list(EXTRACT_FOLDER.glob("*.gdb"))
if not gdbs:
    raise FileNotFoundError("❌ Nenhuma GDB encontrada.")
GDB_PATH = gdbs[0]

# ─── ANALISA CADA CAMADA DE INTERESSE ───────────────────────────
for camada in CAMADAS_ALVO:
    print(f"\n🔍 Camada: {camada}")
    try:
        df = gpd.read_file(GDB_PATH, layer=camada)
        print(f"🔸 {len(df)} linhas | {len(df.columns)} colunas")
        print("🔹 Colunas:", list(df.columns))
    except Exception as e:
        print(f"❌ Erro ao ler {camada}: {e}")
