from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db import get_db
from app.models import ElderlyInfo, Alert, InterventionRecord
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/dashboard", response_model=ResponseBase[dict])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_elderly = (await db.execute(select(func.count(ElderlyInfo.id)))).scalar()
    
    today = datetime.utcnow().date()
    today_alerts = (await db.execute(
        select(func.count(Alert.id)).where(func.date(Alert.created_at) == today)
    )).scalar()
    
    pending_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.status == "pending")
    )).scalar()
    
    critical_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.alert_level == "critical", Alert.status == "pending")
    )).scalar()
    
    return ResponseBase(
        data={
            "total_elderly": total_elderly or 0,
            "today_alerts": today_alerts or 0,
            "pending_alerts": pending_alerts or 0,
            "critical_alerts": critical_alerts or 0,
        }
    )


@router.get("/alerts/statistics", response_model=ResponseBase[dict])
async def get_alert_statistics(db: AsyncSession = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    
    result = await db.execute(
        select(Alert.alert_level, func.count(Alert.id).label("count"))
        .where(Alert.created_at >= start_date)
        .group_by(Alert.alert_level)
    )
    level_stats = {row.alert_level: row.count for row in result}
    
    result = await db.execute(
        select(Alert.status, func.count(Alert.id).label("count"))
        .where(Alert.created_at >= start_date)
        .group_by(Alert.status)
    )
    status_stats = {row.status: row.count for row in result}
    
    return ResponseBase(
        data={
            "by_level": level_stats,
            "by_status": status_stats,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            }
        }
    )


@router.get("/health/overview", response_model=ResponseBase[dict])
async def get_health_overview(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ElderlyInfo))
    elderly_list = result.scalars().all()
    
    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }
    
    import random
    for elderly in elderly_list:
        levels = ["low", "medium", "high", "critical"]
        risk_level = random.choice(levels)
        risk_distribution[risk_level] += 1
    
    return ResponseBase(
        data={
            "total_elderly": len(elderly_list),
            "risk_distribution": risk_distribution,
        }
    )
