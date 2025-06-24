# apps/api/services/lead_service.py
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from packages.database.models import LeadBruto
from apps.api.schemas.lead import LeadMapOut  # importe seu schema, se necessário

async def list_leads(
    db: AsyncSession,
    segment: str | None,
    classe: str | None,
    skip: int,
    limit: int,
):
    query = select(LeadBruto)
    if segment:
        query = query.where(LeadBruto.segmento == segment)
    if classe:
        query = query.where(LeadBruto.classe == classe)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = (await db.execute(query.offset(skip).limit(limit))).scalars().all()
    return total, result

async def get_lead(db: AsyncSession, lead_id: str):
    return await db.get(LeadBruto, lead_id)

async def heatmap_points(db: AsyncSession, segment: str | None):
    query = select(
        LeadBruto.latitude,
        LeadBruto.longitude,
        func.count().label("count"),
    ).group_by(LeadBruto.latitude, LeadBruto.longitude)

    if segment:
        query = query.where(LeadBruto.segmento == segment)

    return (await db.execute(query)).all()

async def get_map_points(db: AsyncSession, status: str | None, distribuidora: str | None, limit: int = 1000):
    filters = ["latitude IS NOT NULL", "longitude IS NOT NULL"]
    params = {"limit": limit}

    if status:
        filters.append("status = :status")
        params["status"] = status
    if distribuidora:
        filters.append("distribuidora = :distribuidora")
        params["distribuidora"] = distribuidora

    where_clause = " AND ".join(filters)
    query = f"""
        SELECT id, latitude, longitude, classe, subgrupo, potencia, distribuidora, status
        FROM lead_bruto
        WHERE {where_clause}
        LIMIT :limit
    """
    stmt = text(query)
    rows = await db.execute(stmt, params)
    return [dict(r._mapping) for r in rows]

async def get_resumo(db: AsyncSession, estado: str | None, municipio: str | None, segmento: str | None):
    filters = []
    params = {}

    if estado:
        filters.append("estado = :estado")
        params["estado"] = estado
    if municipio:
        filters.append("municipio = :municipio")
        params["municipio"] = municipio
    if segmento:
        filters.append("segmento = :segmento")
        params["segmento"] = segmento

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
        SELECT
            COUNT(*) AS total_leads,
            COUNT(cnpj) FILTER (WHERE cnpj IS NOT NULL AND LENGTH(cnpj) = 14) AS total_com_cnpj,
            COUNT(*) FILTER (WHERE status = 'enriched') AS total_enriquecidos,
            ROUND(AVG(ene), 2) AS media_consumo,
            ROUND(AVG(potencia), 2) AS media_potencia
        FROM lead_bruto
        {where_clause}
    """
    r = await db.execute(text(query), params)
    res = dict(r.first()._mapping)

    query2 = f"""
        SELECT classe, COUNT(*) as total
        FROM lead_bruto
        {where_clause}
        GROUP BY classe
    """
    r2 = await db.execute(text(query2), params)
    res["por_classe"] = {row.classe: row.total for row in r2.fetchall() if row.classe}

    return res
