import json
import zipfile
import shutil
import argparse
from pathlib import Path
from urllib.request import urlretrieve

# Caminhos
INDEX_PATH = Path(__file__).resolve().parents[3] / "data/models/aneel_gdb_index.json"
DOWNLOAD_DIR = Path("data/downloads")
TMP_DIR = Path("data/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)

def baixar_arquivo(url: str, destino: Path):
    print(f"⬇️  Baixando: {url}")
    urlretrieve(url, destino)
    print(f"✅ Download salvo em: {destino}")

def extrair_gdb(zip_path: Path, destino_final: Path):
    print(f"📦 Extraindo {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(TMP_DIR)

    for item in TMP_DIR.iterdir():
        if item.suffix == ".gdb" or item.name.endswith(".gdb"):
            final_path = destino_final / item.name
            shutil.move(str(item), final_path)
            print(f"✅ .gdb extraído para: {final_path}")
            break

    zip_path.unlink()
    shutil.rmtree(TMP_DIR, ignore_errors=True)

def baixar_gdb(distribuidora: str, ano: int):
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)

    chave_original = f"{distribuidora}_{ano}"
    chave_normalizada = chave_original.lower().replace(" ", "_").replace("-", "_")

    # Mapeia todas as chaves disponíveis para lower()
    chaves_disponiveis = {k.lower().replace(" ", "_").replace("-", "_"): k for k in index.keys()}

    if chave_normalizada not in chaves_disponiveis:
        raise Exception(f"Distribuidora/ano não encontrado: {chave_original}")

    chave_real = chaves_disponiveis[chave_normalizada]
    url = index[chave_real]

    gdb_name = chave_real + ".gdb"
    gdb_path = DOWNLOAD_DIR / gdb_name

    if gdb_path.exists():
        print(f"⚠️  Já existe: {gdb_path}, pulando download.")
        return

    destino_zip = TMP_DIR / f"{chave_real}.zip"
    baixar_arquivo(url, destino_zip)
    extrair_gdb(destino_zip, DOWNLOAD_DIR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribuidora", required=True)
    parser.add_argument("--ano", required=True, type=int)
    args = parser.parse_args()

    baixar_gdb(args.distribuidora, args.ano)
