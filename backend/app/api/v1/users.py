from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.schemas.common import ResponseBase, PaginatedResponse
from app.core.security import get_password_hash
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=ResponseBase[UserResponse])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return ResponseBase(data=UserResponse.model_validate(current_user))


@router.get("", response_model=ResponseBase[PaginatedResponse[UserResponse]])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)
    count_query = select(func.count(User.id))
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return ResponseBase(
        data=PaginatedResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    )


@router.post("", response_model=ResponseBase[UserResponse])
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="用户名已存在")
    
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        email=user_in.email,
        phone=user_in.phone,
        real_name=user_in.real_name,
        role=user_in.role,
        institution_id=user_in.institution_id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return ResponseBase(data=UserResponse.model_validate(user), message="创建成功")
