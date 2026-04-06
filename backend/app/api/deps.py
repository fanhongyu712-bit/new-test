from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ..db import get_db
from ..models import User
from ..core.security import decode_access_token
from ..core.exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("无效的认证令牌")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("无效的认证令牌")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("用户不存在")
    
    if user.status != "active":
        raise ForbiddenException("用户已被禁用")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status != "active":
        raise ForbiddenException("用户已被禁用")
    return current_user


def check_role(allowed_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("权限不足")
        return current_user
    return role_checker
