#!/usr/bin/env python3
import os
import requests
import zipfile
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import argparse

load_dotenv()

BASE_DIR = Path("data/downloads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def baixar_arquivo(url: str, caminho_zip: Path):
    """Faz download com barra de progresso"""
    response = requests.get(url, stream=True)
    total = int(response.headers.get("content-length", 0))
    
    with open(caminho_zip, "wb") as file, tqdm(
        desc=f"⬇️  Baixando {caminho_zip.name}",
        total=total,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def extrair_zip(caminho_zip: Path, destino: Path):
    """Extrai o conteúdo do ZIP para o destino"""
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(destino)
    print(f"📦 Extraído para: {destino}")

def download_gdb(distribuidora: str, prefixo: str, ano: int, url: str):
    nome_base = f"{prefixo}_{ano}"
    caminho_zip = BASE_DIR / f"{nome_base}.zip"
    destino_gdb = BASE_DIR / f"{nome_base}.gdb"

    if destino_gdb.exists():
        print(f"✅ GDB já extraído: {destino_gdb}")
        return

    if not caminho_zip.exists():
        print(f"🌐 Iniciando download de {distribuidora} ({ano})")
        try:
            baixar_arquivo(url, caminho_zip)
        except Exception as e:
            print(f"❌ Erro no download: {e}")
            return
    else:
        print(f"📦 ZIP já baixado: {caminho_zip.name}")

    try:
        extrair_zip(caminho_zip, BASE_DIR)
    except Exception as e:
        print(f"❌ Erro ao extrair: {e}")
        return

    if destino_gdb.exists():
        print(f"✅ GDB disponível para importação: {destino_gdb}")
    else:
        print("⚠️ GDB não encontrado após extração. Verifique o conteúdo do ZIP.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baixar e extrair GDB da ANEEL")
    parser.add_argument("--distribuidora", required=True)
    parser.add_argument("--prefixo", required=True)
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--url", required=True)

    args = parser.parse_args()
    download_gdb(args.distribuidora, args.prefixo, args.ano, args.url)
