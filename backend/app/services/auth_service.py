from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import User, UserType, UsageLog, UserLimit
from app.schemas.user import UserCreate, UserLogin, TokenData
from app.core.config import settings

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "formu-secret-key-2024"  # 应该从环境变量获取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTP Bearer 认证
security = HTTPBearer()

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    async def create_user(self, user: UserCreate) -> User:
        """创建新用户"""
        # 检查用户名是否已存在
        result = await self.db.execute(select(User).where(User.username == user.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        result = await self.db.execute(select(User).where(User.email == user.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 创建新用户
        hashed_password = self.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
            user_type=user.user_type
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        
        user = await self.get_user_by_username(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

# 依赖注入函数
async def get_auth_service(db: AsyncSession) -> AuthService:
    return AuthService(db)
