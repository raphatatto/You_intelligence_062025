# packages/detectors/geo_utils.py

import requests
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def inferir_coordenadas_endereco(endereco: str) -> dict:
    """
    Usa a API do Google Maps para obter lat/lng, CEP, bairro, cidade e UF a partir do endereço textual.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        raise Exception("Erro na requisição à API do Google Maps")

    data = res.json()
    if not data["results"]:
        return {}

    result = data["results"][0]
    location = result["geometry"]["location"]

    componentes = result["address_components"]
    componentes_dict = {item["types"][0]: item["long_name"] for item in componentes}

    return {
        "latitude": location["lat"],
        "longitude": location["lng"],
        "cep": componentes_dict.get("postal_code"),
        "bairro": componentes_dict.get("sublocality") or componentes_dict.get("neighborhood"),
        "municipio": componentes_dict.get("administrative_area_level_2"),
        "uf": componentes_dict.get("administrative_area_level_1")
    }