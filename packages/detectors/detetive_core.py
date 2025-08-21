from .geo_utils import inferir_coordenadas_endereco
from .cnpj_utils import buscar_dados_empresa
from .match_engine import buscar_uc_por_ponto_geografico
from .diagnoser import diagnosticar_uc


def montar_dossie_detetive(dados_input: dict, db):
    """
    Pipeline principal do modo Detetive. Recebe dados parciais e tenta montar um dossiê completo.
    """
    resultado = {
        "entrada": dados_input,
        "logs": [],
        "etapas": {},
        "possiveis_matches": [],
        "match_principal": None,
        "diagnostico": None,
        "score_confianca": 0.0
    }

    try:
        # Etapa 1 - Buscar dados da empresa (se houver CNPJ ou nome)
        if dados_input.get("cnpj") or dados_input.get("nome"):
            empresa = buscar_dados_empresa(dados_input)
            resultado["etapas"]["empresa"] = empresa
            resultado["logs"].append("Empresa localizada via CNPJá.")
            if not dados_input.get("endereco") and empresa.get("endereco"):
                dados_input["endereco"] = empresa["endereco"]
        else:
            resultado["logs"].append("Nenhum CNPJ ou nome informado para buscar dados empresariais.")

        # Etapa 2 - Inferir coordenadas e CEP se tiver endereço
        if dados_input.get("endereco"):
            geo = inferir_coordenadas_endereco(dados_input["endereco"])
            resultado["etapas"]["geo"] = geo
            dados_input.update(geo)
            resultado["logs"].append("Endereço geocodificado com sucesso.")
        else:
            resultado["logs"].append("Endereço não informado. Pulo geocodificação.")

        # Etapa 3 - Buscar possível UC na base ANEEL via ponto geográfico
        matches = buscar_uc_por_ponto_geografico(dados_input, db)
        resultado["possiveis_matches"] = matches

        if matches:
            match = matches[0]
            resultado["match_principal"] = match
            resultado["logs"].append(f"UC encontrada com distância aproximada de {round(match.get('distancia_metros', 0), 2)} metros.")
        else:
            resultado["logs"].append("Nenhuma UC correspondente encontrada na base.")
            return resultado

        # Etapa 4 - Diagnóstico da UC encontrada
        diagnostico = diagnosticar_uc(match["uc_id"], db)
        resultado["diagnostico"] = diagnostico

        # Etapa 5 - Score de confiança
        score = 0
        if dados_input.get("cnpj") and resultado["etapas"].get("empresa"):
            score += 30
        if dados_input.get("endereco"):
            score += 25
        if dados_input.get("cep"):
            score += 10
        if dados_input.get("latitude") and dados_input.get("longitude"):
            score += 30
        if diagnostico:
            score += 25

        resultado["score_confianca"] = min(score, 100.0)

    except Exception as e:
        resultado["logs"].append(f"Erro durante análise: {str(e)}")

    # ✅ Garantia de tipos corretos para evitar erro no response_model
    resultado["possiveis_matches"] = resultado.get("possiveis_matches", []) or []
    resultado["match_principal"] = resultado.get("match_principal") or None
    resultado["diagnostico"] = resultado.get("diagnostico") or None
    resultado["logs"] = resultado.get("logs", []) or []

    return resultado
