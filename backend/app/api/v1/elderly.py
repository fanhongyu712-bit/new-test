from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date

from app.db import get_db
from app.models import ElderlyInfo, HealthRecord
from app.schemas import ElderlyCreate, ElderlyUpdate, ElderlyResponse, HealthRecordCreate, HealthRecordResponse
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter()


@router.get("/health-records", response_model=ResponseBase[PaginatedResponse[HealthRecordResponse]])
async def list_health_records(
    elderly_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(HealthRecord).where(HealthRecord.elderly_id == elderly_id)
    count_query = select(func.count(HealthRecord.id)).where(HealthRecord.elderly_id == elderly_id)
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(HealthRecord.record_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[HealthRecordResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.get("", response_model=ResponseBase[PaginatedResponse[ElderlyResponse]])
async def list_elderly(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ElderlyInfo)
    count_query = select(func.count(ElderlyInfo.id))
    
    if name:
        query = query.where(ElderlyInfo.name.ilike(f"%{name}%"))
        count_query = count_query.where(ElderlyInfo.name.ilike(f"%{name}%"))
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    elderly_list = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[ElderlyResponse.model_validate(e) for e in elderly_list],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.get("/{elderly_id}", response_model=ResponseBase[ElderlyResponse])
async def get_elderly(elderly_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    return ResponseBase(data=ElderlyResponse.model_validate(elderly))


@router.post("", response_model=ResponseBase[ElderlyResponse])
async def create_elderly(elderly_in: ElderlyCreate, db: AsyncSession = Depends(get_db)):
    elderly = ElderlyInfo(**elderly_in.model_dump())
    
    db.add(elderly)
    await db.commit()
    await db.refresh(elderly)
    
    return ResponseBase(data=ElderlyResponse.model_validate(elderly), message="创建成功")


@router.put("/{elderly_id}", response_model=ResponseBase[ElderlyResponse])
async def update_elderly(elderly_id: str, elderly_in: ElderlyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    update_data = elderly_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(elderly, field, value)
    
    await db.commit()
    await db.refresh(elderly)
    
    return ResponseBase(data=ElderlyResponse.model_validate(elderly), message="更新成功")


@router.delete("/{elderly_id}", response_model=ResponseBase)
async def delete_elderly(elderly_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    elderly.status = "inactive"
    await db.commit()
    
    return ResponseBase(message="删除成功")
