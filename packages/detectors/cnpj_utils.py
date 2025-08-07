# packages/detectors/cnpj_utils.py

import requests
import re
import os

CNPJA_TOKEN = os.getenv("CNPJA_API_TOKEN")  # sua chave comercial vai no .env


def limpar_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def buscar_dados_empresa(dados: dict) -> dict:
    """
    Usa a API comercial da CNPJá com token, consultando por CNPJ ou nome.
    """
    headers = {"Authorization": f"Bearer {CNPJA_TOKEN}"}
    base_url = "https://api.cnpja.com.br/companies"

    if dados.get("cnpj"):
        cnpj = limpar_cnpj(dados["cnpj"])
        url = f"{base_url}/{cnpj}"
    elif dados.get("nome"):
        nome = dados["nome"]
        url = f"{base_url}?search={nome}"
    else:
        return {}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return {}

    data = res.json()
    if isinstance(data, list):
        data = data[0] if data else {}

    endereco = data.get("address", {})

    return {
        "razao_social": data.get("company", {}).get("name"),
        "nome_fantasia": data.get("alias"),
        "cnpj": data.get("taxId"),
        "cnae": data.get("mainActivity", {}).get("id"),
        "cnae_descricao": data.get("mainActivity", {}).get("text"),
        "email": data.get("emails", [{}])[0].get("address"),
        "telefone": data.get("phones", [{}])[0].get("number"),
        "endereco": f"{endereco.get('street', '')}, {endereco.get('number', '')}, {endereco.get('district', '')}, {endereco.get('city', '')} - {endereco.get('state', '')}"
    }
