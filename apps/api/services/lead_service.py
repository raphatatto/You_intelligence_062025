from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from packages.database.models import LeadBruto

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
