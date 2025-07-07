# packages/jobs/utils/sanitizadores.py

import pandas as pd

def sanitize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte as colunas de um DataFrame para numérico (float), tratando strings inválidas.
    Tudo que não conseguir ser convertido vira NaN.
    """
    return df.apply(pd.to_numeric, errors="coerce")
