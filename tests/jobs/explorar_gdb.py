import geopandas as gpd
import fiona
import json
from pathlib import Path

def explorar_gdb(gdb_path: str, salvar_json: bool = True) -> dict:
    path = Path(gdb_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo GDB não encontrado em: {gdb_path}")

    print(f"📂 Explorando Geodatabase: {gdb_path}")
    
    metadata = {}
    layers = fiona.listlayers(path)
    print(f"🔍 {len(layers)} camadas encontradas: {layers}")

    for layer in layers:
        try:
            df = gpd.read_file(gdb_path, layer=layer, rows=1)
            metadata[layer] = list(df.columns)
            print(f"✅ {layer}: {len(df.columns)} colunas")
        except Exception as e:
            metadata[layer] = f"Erro: {str(e)}"
            print(f"❌ {layer}: Erro ao ler - {str(e)}")

    if salvar_json:
        output = path.parent / f"{path.stem}_estruturado.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON salvo em: {output}")

    return metadata


if __name__ == "__main__":
    # Exemplo: substitua com o caminho local completo do seu GDB
    gdb_path = "data/downloads/Enel_RJ_383_2023-12-31_V11_20250112-1903.gdb"
    resultado = explorar_gdb(gdb_path)