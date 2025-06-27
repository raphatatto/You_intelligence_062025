import pandas as pd
import json
from pathlib import Path

CSV_PATH = Path("data/downloads/aneel_catalogo_arcgis.csv")
OUTPUT_PATH = Path("data/models/aneel_gdb_index.json")

def extrair_distribuidora_ano(title: str) -> tuple[str, int]:
    try:
        partes = title.split(" - ")
        distribuidora = partes[0].strip()
        ano = int(partes[1].split("-")[0])
        return distribuidora, ano
    except Exception:
        return "DESCONHECIDO", 0

def processar_catalogo():
    df = pd.read_csv(CSV_PATH)
    registros = []

    for _, row in df.iterrows():
        distribuidora, ano = extrair_distribuidora_ano(str(row["title"]))
        dataset_id = row["id"]
        url_download = f"https://www.arcgis.com/sharing/rest/content/items/{dataset_id}/data"

        registros.append({
            "distribuidora": distribuidora,
            "ano": ano,
            "id": dataset_id,
            "download": url_download,
            "created": row["created"],
            "modified": row["modified"]
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(registros)} registros processados.")
    print(f"📁 JSON salvo em: {OUTPUT_PATH.resolve()}")

if __name__ == "__main__":
    processar_catalogo()
