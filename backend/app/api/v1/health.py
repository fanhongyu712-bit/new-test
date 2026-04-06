from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta
import random

from app.db import get_db
from app.models import HealthMetric, Device, ElderlyInfo
from app.schemas import HealthMetricResponse, DeviceCreate, DeviceResponse, HealthTrendResponse
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter()


@router.get("/metrics", response_model=ResponseBase[list[HealthMetricResponse]])
async def list_health_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthMetric))
    metrics = result.scalars().all()
    
    return ResponseBase(data=[HealthMetricResponse.model_validate(m) for m in metrics])


@router.get("/devices", response_model=ResponseBase[PaginatedResponse[DeviceResponse]])
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Device)
    count_query = select(func.count(Device.id))
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[DeviceResponse.model_validate(d) for d in devices],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.get("/data/{elderly_id}/trend", response_model=ResponseBase[HealthTrendResponse])
async def get_health_trend(
    elderly_id: str,
    metric_code: str = Query(...),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HealthMetric).where(HealthMetric.code == metric_code))
    metric = result.scalar_one_or_none()
    if not metric:
        return ResponseBase(code=404, message="健康指标不存在")
    
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=7)
    if not end_time:
        end_time = datetime.utcnow()
    
    data_points = []
    values = []
    
    current_time = start_time
    while current_time <= end_time:
        base_value = float(metric.normal_min + metric.normal_max) / 2 if metric.normal_min and metric.normal_max else 50
        value = base_value + random.uniform(-10, 10)
        
        data_points.append({
            "time": current_time.isoformat(),
            "value": round(value, 2),
        })
        values.append(value)
        current_time += timedelta(hours=1)
    
    statistics = {
        "count": len(values),
        "min": round(min(values), 2) if values else None,
        "max": round(max(values), 2) if values else None,
        "avg": round(sum(values) / len(values), 2) if values else None,
    }
    
    return ResponseBase(
        data=HealthTrendResponse(
            metric_code=metric_code,
            metric_name=metric.name,
            unit=metric.unit,
            data=data_points,
            statistics=statistics,
        )
    )


@router.get("/data/{elderly_id}/latest", response_model=ResponseBase[dict])
async def get_latest_health_data(elderly_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthMetric))
    metrics = result.scalars().all()
    
    latest_data = {}
    
    for metric in metrics:
        base_value = float(metric.normal_min + metric.normal_max) / 2 if metric.normal_min and metric.normal_max else 50
        value = base_value + random.uniform(-5, 5)
        
        latest_data[metric.code] = {
            "name": metric.name,
            "value": round(value, 2),
            "unit": metric.unit,
            "time": datetime.utcnow().isoformat(),
        }
    
    return ResponseBase(data=latest_data)
