from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models import InterventionPlan, InterventionRecord
from app.schemas import InterventionPlanCreate, InterventionPlanResponse, InterventionRecordCreate, InterventionRecordUpdate, InterventionRecordResponse
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter()


@router.get("/plans", response_model=ResponseBase[PaginatedResponse[InterventionPlanResponse]])
async def list_intervention_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(InterventionPlan)
    count_query = select(func.count(InterventionPlan.id))
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[InterventionPlanResponse.model_validate(p) for p in plans],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.get("/records", response_model=ResponseBase[PaginatedResponse[InterventionRecordResponse]])
async def list_intervention_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    elderly_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(InterventionRecord)
    count_query = select(func.count(InterventionRecord.id))
    
    if elderly_id:
        query = query.where(InterventionRecord.elderly_id == elderly_id)
        count_query = count_query.where(InterventionRecord.elderly_id == elderly_id)
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(InterventionRecord.start_time.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[InterventionRecordResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.post("/records", response_model=ResponseBase[InterventionRecordResponse])
async def create_intervention_record(record_in: InterventionRecordCreate, db: AsyncSession = Depends(get_db)):
    record = InterventionRecord(**record_in.model_dump())
    
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return ResponseBase(data=InterventionRecordResponse.model_validate(record), message="创建成功")
