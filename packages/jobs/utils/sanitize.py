import pandas as pd
import numpy as np
import re

def safe_series_sanitizer(fn):
    def wrapper(serie):
        if isinstance(serie, pd.Series):
            return fn(serie)
        try:
            return fn(pd.Series([serie])).iloc[0]
        except:
            return None
    return wrapper


def sanitize_numeric(serie, errors="coerce"):
    """
    Limpa strings numéricas com vírgula, traços, textos, 'None', 'nan', etc., e converte para float.
    Suporta notações com erro de OCR ou símbolos diversos. Ideal para PAC, DEM_CONT, SEMRED.
    """
    null_set = {"", "none", "nan", "-", "***", "n/a", "null"}

    if isinstance(serie, pd.Series):
        return (
            serie
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(r"[^\d.\-eE+]", "", regex=True)
            .str.strip()
            .apply(lambda x: np.nan if x.lower() in null_set else x)
            .apply(lambda x: pd.to_numeric(x, errors=errors))
        )

    elif isinstance(serie, str):
        cleaned = re.sub(r"[^\d.\-eE+]", "", serie.replace(",", ".")).strip()
        if cleaned.lower() in null_set:
            return np.nan
        try:
            return float(cleaned)
        except:
            return np.nan

    else:
        try:
            return float(serie)
        except:
            return np.nan


@safe_series_sanitizer
def sanitize_str(serie):
    """
    Remove caracteres de controle e espaços desnecessários.
    """
    return (
        serie
        .astype(str)
        .str.replace(r"[\r\n\t]+", " ", regex=True)
        .str.strip()
    )


@safe_series_sanitizer
def sanitize_cnae(serie):
    """
    Remove traços, barras e converte CNAE para inteiro, quando possível.
    """
    return (
        serie
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .replace("", np.nan)
        .astype("Int64")
    )


@safe_series_sanitizer
def sanitize_int(serie):
    """
    Remove tudo que não for número e converte para Int64.
    """
    return (
        serie
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .replace("", np.nan)
        .astype("Int64")
    )


def sanitize_grupo_tensao(val: str | None) -> str | None:
    if not val:
        return None
    val = str(val).strip().upper()
    mapa = {
        "AT": "AT4", "AT4": "AT4", "AT3": "AT3", "AT2": "AT2",
        "MT": "MT3", "MT3": "MT3", "MT2": "MT2", "MT1": "MT1",
        "BT": "BT2", "BT2": "BT2", "BT1": "BT1",
    }
    return mapa.get(val, val)


def sanitize_modalidade(val: str | None) -> str | None:
    if not val:
        return None
    val = str(val).strip().upper()
    base_match = re.match(r"^(A1|A2|A3A|A3|A4|AS|B1|B2|B3|B4)", val)
    if base_match:
        val = base_match.group(0)
    mapa = {
        "CONVENCIONAL": "Convencional", "AZUL": "Azul", "VERDE": "Verde", "BRANCA": "Branca",
        "B1": "B1", "B2": "B2", "B3": "B3", "B4": "B4",
        "A1": "A1", "A2": "A2", "A3": "A3", "A3A": "A3a", "A4": "A4", "AS": "AS"
    }
    return mapa.get(val, val.title())


def sanitize_tipo_sistema(val: str | None) -> str | None:
    if not val:
        return None
    val = str(val).strip().upper()
    mapa = {
        "TRIFÁSICO": "Trifásico", "BIFÁSICO": "Bifásico", "MONOFÁSICO": "Monofásico",
        "TRIFASICO": "Trifásico", "BIFASICO": "Bifásico", "MONOFASICO": "Monofásico",
        "RD_INTERLIG": "RD_INTERLIG", "RD_ISOLADA": "RD_ISOLADA",
        "GER_LOCAL": "GER_LOCAL", "NA": "NA"
    }
    return mapa.get(val, val)


def sanitize_situacao(val: str | None) -> str | None:
    if not val:
        return None
    val = str(val).strip().upper()
    mapa = {
        "AT": "ATIVA", "IN": "INATIVA", "CO": "CORTADA", "SU": "SUPRIMIDA",
        "EM": "EM_IMPLANTAÇÃO", "DE": "DESATIVADA", "DS": "DESATIVADA",
        "IM": "EM_IMPLANTAÇÃO",
        "ATIVA": "ATIVA", "INATIVA": "INATIVA", "CORTADA": "CORTADA",
        "SUPRIMIDA": "SUPRIMIDA", "EM_IMPLANTAÇÃO": "EM_IMPLANTAÇÃO", "DESATIVADA": "DESATIVADA"
    }
    return mapa.get(val, val)


def sanitize_classe(val: str | None) -> str | None:
    if not val:
        return None
    val = str(val).strip().upper()

    if val in ["CSPS", "RUB", "CPR", "CPRVE", "CPRSP", "CPRVC", "CPRAC", "CPRS", "CP", "COM", "COMERCIAL_1"]:
        return "COMERCIAL"
    if val in ["RE_BPC", "RE_BEN", "REKQ", "REIND", "RE", "RE1", "RE2", "RE3"]:
        return "RESIDENCIAL"
    if val in ["IN", "IN2", "IN3", "IND", "INDUS", "INDUSTRIA"]:
        return "INDUSTRIAL"
    if val in ["PP", "PP1", "PP2", "P_P", "PÚBLICO", "PODER"]:
        return "PODER_PÚBLICO"
    if val in ["IP", "ILUM", "ILUMP", "ILUMINAÇÃO"]:
        return "ILUMINAÇÃO_PÚBLICA"
    if val in ["RU", "RUR", "RUB", "RU_IRR", "RUAGR", "RURAL_1"]:
        return "RURAL"
    if val in ["SP", "CSPS", "SERV", "SERVICO", "SERVIÇO"]:
        return "SERVIÇO_PÚBLICO"
    if val in ["CPRO", "AUTO", "CONSUMO_PROPRIO", "GERACAO"]:
        return "CONSUMO_PRÓPRIO"

    base = ''.join([c for c in val if not c.isdigit()])

    if base.startswith("RE"):
        return "RESIDENCIAL"
    if base.startswith("CO") or base.startswith("CPR"):
        return "COMERCIAL"
    if base.startswith("IN"):
        return "INDUSTRIAL"
    if base.startswith("PP"):
        return "PODER_PÚBLICO"
    if base.startswith("IP"):
        return "ILUMINAÇÃO_PÚBLICA"
    if base.startswith("RU"):
        return "RURAL"
    if base.startswith("SP") or base.startswith("CS"):
        return "SERVIÇO_PÚBLICO"

    return base


def sanitize_pac(value):
    try:
        val = float(value)
        return int(val) if 0 < val < 1_000_000 else None  # aceita até 1 MW
    except:
        return None
