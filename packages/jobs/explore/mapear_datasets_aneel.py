import requests
import json

URL = "https://dadosabertos-aneel.opendata.arcgis.com/data.json"
OUTFILE = "aneel_datasets.json"

def main():
    print("🔍 Baixando catálogo completo da ANEEL...")
    resp = requests.get(URL, verify=False)
    resp.raise_for_status()

    catalog = resp.json()
    datasets = []

    for item in catalog.get("dataset", []):
        dataset = {
            "title": item.get("title"),
            "description": item.get("description"),
            "tags": item.get("keyword"),
            "updated": item.get("modified"),
            "resources": []
        }

        for dist in item.get("distribution", []):
            dataset["resources"].append({
                "name": dist.get("title"),
                "format": dist.get("format"),
                "url": dist.get("downloadURL") or dist.get("accessURL")
            })

        datasets.append(dataset)

    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(datasets, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(datasets)} datasets salvos em {OUTFILE}")

if __name__ == "__main__":
    main()



