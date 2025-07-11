# tests/test_sanitize.py

import numpy as np
import pandas as pd
import pytest

from packages.jobs.utils.sanitizadores import (
    sanitize_numeric,
    sanitize_cnae,
    sanitize_int,
    sanitize_str,
    sanitize_grupo_tensao,
    sanitize_modalidade,
    sanitize_tipo_sistema,
    sanitize_situacao,
    sanitize_classe
)

def test_sanitize_numeric_series():
    serie = pd.Series(["1.234,56", "2.000", "***", "nan", "-123,45", None])
    resultado = sanitize_numeric(serie)
    assert resultado.tolist() == [1234.56, 2000.0, np.nan, np.nan, -123.45, np.nan]

def test_sanitize_numeric_single_string():
    assert sanitize_numeric("1.234,56") == 1234.56
    assert np.isnan(sanitize_numeric("nan"))
    assert sanitize_numeric("-400") == -400.0

def test_sanitize_cnae():
    serie = pd.Series(["1234-5/01", "5678-9/02", None, "***"])
    resultado = sanitize_cnae(serie)
    assert resultado.tolist() == [1234, 5678, pd.NA, pd.NA]

def test_sanitize_int():
    serie = pd.Series(["123", "abc456", "78-90", None])
    resultado = sanitize_int(serie)
    assert resultado.tolist() == [123, 456, 7890, pd.NA]

def test_sanitize_str():
    serie = pd.Series(["  teste\t", "\nvalor\r", "ok"])
    resultado = sanitize_str(serie)
    assert resultado.tolist() == ["teste", "valor", "ok"]

def test_grupo_tensao():
    assert sanitize_grupo_tensao("MT") == "MT3"
    assert sanitize_grupo_tensao("BT2") == "BT2"
    assert sanitize_grupo_tensao(None) is None

def test_modalidade():
    assert sanitize_modalidade("B1") == "B1"
    assert sanitize_modalidade("B2Ru") == "B2"
    assert sanitize_modalidade("azul") == "Azul"

def test_tipo_sistema():
    assert sanitize_tipo_sistema("TRIFASICO") == "Trifásico"
    assert sanitize_tipo_sistema("MONOFÁSICO") == "Monofásico"
    assert sanitize_tipo_sistema(None) is None

def test_situacao():
    assert sanitize_situacao("AT") == "ATIVA"
    assert sanitize_situacao("CO") == "CORTADA"
    assert sanitize_situacao("inativa") == "INATIVA"

def test_classe():
    assert sanitize_classe("RE") == "RESIDENCIAL"
    assert sanitize_classe("CPR") == "COMERCIAL"
    assert sanitize_classe("IND") == "INDUSTRIAL"
    assert sanitize_classe("IP") == "ILUMINAÇÃO_PÚBLICA"
