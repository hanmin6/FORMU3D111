from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService, get_auth_service, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.usage_service import UsageService, get_usage_service
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, UserStatus
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

# 认证服务实例用于依赖注入

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    try:
        auth_service = AuthService(db)
        db_user = await auth_service.create_user(user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user

@router.get("/status", response_model=UserStatus)
async def get_user_status(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户状态信息（包括使用次数等）"""
    usage_service = UsageService(db)
    return await usage_service.get_user_status(current_user)
