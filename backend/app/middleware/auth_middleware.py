from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import JWTError, jwt

from app.core.database import get_db
from app.services.auth_service import AuthService, SECRET_KEY, ALGORITHM
from app.services.usage_service import UsageService
from app.models.user import User, UserType

# HTTP Bearer 认证
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

async def check_usage_limit(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """检查用户使用次数限制"""
    usage_service = UsageService(db)
    
    # 检查本周使用次数
    usage_this_week = await usage_service.get_usage_this_week(current_user.id)
    user_limit = await usage_service.get_user_limit(current_user.user_type)
    
    if user_limit.weekly_limit != -1 and usage_this_week >= user_limit.weekly_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"本周使用次数已达上限 ({user_limit.weekly_limit} 次)，请下周再试"
        )
    
    return current_user

async def check_3d_permission(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """检查3D功能权限"""
    usage_service = UsageService(db)
    user_limit = await usage_service.get_user_limit(current_user.user_type)
    
    if not user_limit.can_use_3d:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限使用3D建模功能，请联系管理员升级账户"
        )
    
    return current_user

async def check_prompt_permission(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """检查提示词查看权限"""
    usage_service = UsageService(db)
    user_limit = await usage_service.get_user_limit(current_user.user_type)
    
    if not user_limit.can_see_prompts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看提示词生成过程"
        )
    
    return current_user

# 依赖注入函数
async def get_usage_service(db: AsyncSession = Depends(get_db)) -> UsageService:
    return UsageService(db)
