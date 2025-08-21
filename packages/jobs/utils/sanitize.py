import pandas as pd
import numpy as np
import re

# --------------------------------------------------------------------------------------
# Decorator: permite que a mesma função aceite escalar OU Series sem quebrar comportamento.
# --------------------------------------------------------------------------------------
def safe_series_sanitizer(fn):
    def wrapper(serie):
        if isinstance(serie, pd.Series):
            return fn(serie)
        try:
            return fn(pd.Series([serie])).iloc[0]
        except Exception:
            return None
    return wrapper

# --------------------------------------------------------------------------------------
# Numérico
# --------------------------------------------------------------------------------------
def sanitize_numeric(serie, errors="coerce"):
    """
    Limpa strings numéricas com vírgula, traços, textos, 'None', 'nan', etc., e converte para float.
    Suporta notações com erro de OCR ou símbolos diversos. Ideal para PAC, DEM_CONT, SEMRED.
    """
    null_set = {"", "none", "nan", "-", "***", "n/a", "null", "None", "NaN", "NULL"}

    if isinstance(serie, pd.Series):
        s = (
            serie.astype(str)
                 .str.replace(",", ".", regex=False)
                 .str.replace(r"[^\d.\-eE+]", "", regex=True)
                 .str.strip()
        )
        s = s.apply(lambda x: np.nan if x.lower() in {z.lower() for z in null_set} else x)
        return pd.to_numeric(s, errors=errors)

    # escalar
    if serie is None:
        return np.nan
    try:
        cleaned = re.sub(r"[^\d.\-eE+]", "", str(serie).replace(",", ".")).strip()
        if cleaned.lower() in {z.lower() for z in null_set} or cleaned == "":
            return np.nan
        return float(cleaned)
    except Exception:
        return np.nan

# --------------------------------------------------------------------------------------
# Strings e inteiros básicos (já eram vetorizadas)
# --------------------------------------------------------------------------------------
@safe_series_sanitizer
def sanitize_str(serie):
    """Remove caracteres de controle e espaços desnecessários."""
    return (
        serie.astype(str)
             .str.replace(r"[\r\n\t]+", " ", regex=True)
             .str.strip()
    )

@safe_series_sanitizer
def sanitize_cnae(serie):
    """Remove traços, barras e converte CNAE para inteiro, quando possível."""
    return (
        serie.astype(str)
             .str.extract(r"(\d+)", expand=False)
             .replace("", np.nan)
             .astype("Int64")
    )

@safe_series_sanitizer
def sanitize_int(serie):
    """Remove tudo que não for número e converte para Int64."""
    return (
        serie.astype(str)
             .str.replace(r"[^\d]", "", regex=True)
             .replace("", np.nan)
             .astype("Int64")
    )

# --------------------------------------------------------------------------------------
# Categóricos: agora 100% seguros para Series OU escalares (UCBT não quebra mais)
# --------------------------------------------------------------------------------------
@safe_series_sanitizer
def sanitize_grupo_tensao(serie: pd.Series) -> pd.Series:
    """
    Normaliza GRU_TEN para domínios padronizados.
    Aceita valores como 'AT', 'MT', 'BT' e variantes mapeadas.
    """
    mapa = {
        "AT": "AT4", "AT4": "AT4", "AT3": "AT3", "AT2": "AT2",
        "MT": "MT3", "MT3": "MT3", "MT2": "MT2", "MT1": "MT1",
        "BT": "BT2", "BT2": "BT2", "BT1": "BT1",
    }
    s = serie.astype(str).str.strip().str.upper()
    s = s.replace({"": None, "NAN": None, "NONE": None})
    return s.map(mapa).fillna(s).where(s.notna(), None)

@safe_series_sanitizer
def sanitize_modalidade(serie: pd.Series) -> pd.Series:
    """
    Normaliza modalidade tarifária (grupo/subgrupo).
    Mantém compatibilidade com o comportamento anterior (regex A1, A2, A3A, A3, A4, AS, B1..B4).
    """
    base_map = {
        "CONVENCIONAL": "Convencional", "AZUL": "Azul", "VERDE": "Verde", "BRANCA": "Branca",
        "B1": "B1", "B2": "B2", "B3": "B3", "B4": "B4",
        "A1": "A1", "A2": "A2", "A3": "A3", "A3A": "A3a", "A4": "A4", "AS": "AS"
    }

    s = serie.astype(str).str.strip().str.upper()
    s = s.replace({"": None, "NAN": None, "NONE": None})

    # Extrai prefixo quando começar por subgrupo A/B
    prefix = s.str.extract(r"^(A1|A2|A3A|A3|A4|AS|B1|B2|B3|B4)", expand=False)
    s2 = prefix.fillna(s)

    # Aplica mapa (respeitando capitalização pedida)
    out = s2.map(base_map).fillna(s2.str.title())
    return out.where(s.notna(), None)

@safe_series_sanitizer
def sanitize_tipo_sistema(serie: pd.Series) -> pd.Series:
    """
    Normaliza tipo de sistema (TRIFÁSICO/BIFÁSICO/MONOFÁSICO/RD_* etc.).
    """
    mapa = {
        "TRIFÁSICO": "Trifásico", "BIFÁSICO": "Bifásico", "MONOFÁSICO": "Monofásico",
        "TRIFASICO": "Trifásico", "BIFASICO": "Bifásico", "MONOFASICO": "Monofásico",
        "RD_INTERLIG": "RD_INTERLIG", "RD_ISOLADA": "RD_ISOLADA",
        "GER_LOCAL": "GER_LOCAL", "NA": "NA"
    }
    s = serie.astype(str).str.strip().str.upper()
    s = s.replace({"": None, "NAN": None, "NONE": None})
    return s.map(mapa).fillna(s).where(s.notna(), None)

@safe_series_sanitizer
def sanitize_situacao(serie: pd.Series) -> pd.Series:
    """
    Normaliza situação da UC.
    """
    mapa = {
        "AT": "ATIVA", "IN": "INATIVA", "CO": "CORTADA", "SU": "SUPRIMIDA",
        "EM": "EM_IMPLANTAÇÃO", "DE": "DESATIVADA", "DS": "DESATIVADA",
        "IM": "EM_IMPLANTAÇÃO",
        "ATIVA": "ATIVA", "INATIVA": "INATIVA", "CORTADA": "CORTADA",
        "SUPRIMIDA": "SUPRIMIDA", "EM_IMPLANTAÇÃO": "EM_IMPLANTAÇÃO", "DESATIVADA": "DESATIVADA"
    }
    s = serie.astype(str).str.strip().str.upper()
    s = s.replace({"": None, "NAN": None, "NONE": None})
    return s.map(mapa).fillna(s).where(s.notna(), None)

def _sanitize_classe_single(val: str | None) -> str | None:
    if not val:
        return None
    v = str(val).strip().upper()

    if v in ["CSPS", "RUB", "CPR", "CPRVE", "CPRSP", "CPRVC", "CPRAC", "CPRS", "CP", "COM", "COMERCIAL_1"]:
        return "COMERCIAL"
    if v in ["RE_BPC", "RE_BEN", "REKQ", "REIND", "RE", "RE1", "RE2", "RE3"]:
        return "RESIDENCIAL"
    if v in ["IN", "IN2", "IN3", "IND", "INDUS", "INDUSTRIA"]:
        return "INDUSTRIAL"
    if v in ["PP", "PP1", "PP2", "P_P", "PÚBLICO", "PODER"]:
        return "PODER_PÚBLICO"
    if v in ["IP", "ILUM", "ILUMP", "ILUMINAÇÃO"]:
        return "ILUMINAÇÃO_PÚBLICA"
    if v in ["RU", "RUR", "RUB", "RU_IRR", "RUAGR", "RURAL_1"]:
        return "RURAL"
    if v in ["SP", "CSPS", "SERV", "SERVICO", "SERVIÇO"]:
        return "SERVIÇO_PÚBLICO"
    if v in ["CPRO", "AUTO", "CONSUMO_PROPRIO", "GERACAO"]:
        return "CONSUMO_PRÓPRIO"

    base = ''.join([c for c in v if not c.isdigit()])

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

    return base or None

@safe_series_sanitizer
def sanitize_classe(serie: pd.Series) -> pd.Series:
    """
    Normaliza classe da UC. Mantém semântica anterior, porém seguro para Series.
    """
    s = serie.where(pd.notnull(serie), None)
    return s.apply(_sanitize_classe_single)

# --------------------------------------------------------------------------------------
# Específicos
# --------------------------------------------------------------------------------------
@safe_series_sanitizer
def sanitize_pac(serie):
    """
    Mantido exatamente como estava, apenas com o decorator para aceitar escalar/Series.
    """
    return (
        pd.to_numeric(serie, errors="coerce")
          .apply(lambda x: int(x) if pd.notnull(x) and 0 < x < 1_000_000 else None)
          .astype("Int64")
    )
