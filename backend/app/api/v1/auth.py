from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db import get_db
from app.models import User
from app.schemas import Token
from app.schemas.common import ResponseBase
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=ResponseBase[Token])
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if user.status != "active":
        raise HTTPException(status_code=401, detail="用户已被禁用")
    
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    access_token = create_access_token(subject=str(user.id))
    
    return ResponseBase(data=Token(access_token=access_token), message="登录成功")


@router.post("/logout", response_model=ResponseBase)
async def logout():
    return ResponseBase(message="退出成功")
