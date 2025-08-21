from sqlalchemy import text

def buscar_uc_por_ponto_geografico(dados: dict, db, limit: int = 10, raio_max_metros: float = 100.0) -> list:
    """
    Busca unidades consumidoras mais próximas com base em coordenadas geográficas.
    Retorna apenas as que estão dentro do raio máximo permitido.
    """
    lat = dados.get("latitude")
    lng = dados.get("longitude")

    if not lat or not lng:
        return []

    query = text(f"""
        SELECT *,
            ST_Distance(
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            ) AS distancia_metros
        FROM intel_lead.vw_lead_completo_detalhado
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY distancia_metros ASC
        LIMIT {limit}
    """)

    res = db.execute(query, {"lat": lat, "lng": lng})
    rows = res.fetchall()

    # Filtra e classifica os matches dentro do raio
    matches = []
    for row in rows:
        row_dict = dict(row)
        distancia = row_dict.get("distancia_metros", 9999)

        if distancia <= raio_max_metros:
            row_dict["nivel_match"] = _classificar_match_por_distancia(distancia)
            matches.append(row_dict)

    return matches

def _classificar_match_por_distancia(distancia: float) -> str:
    """
    Retorna um nível de confiança baseado na distância.
    """
    if distancia <= 10:
        return "exato"
    elif distancia <= 30:
        return "muito_proximo"
    elif distancia <= 60:
        return "proximo"
    elif distancia <= 100:
        return "distante"
    else:
        return "fora_do_limite"
