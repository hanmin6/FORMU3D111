from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserType

# 用户注册/登录相关
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_type: UserType = UserType.SPARK_PARTNER

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    user_type: UserType
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token 相关
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# 使用记录相关
class UsageLogCreate(BaseModel):
    workflow_type: str
    image_url: Optional[str] = None
    result_url: Optional[str] = None

class UsageLogResponse(BaseModel):
    id: int
    user_id: int
    workflow_type: str
    image_url: Optional[str]
    result_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户限制相关
class UserLimitResponse(BaseModel):
    user_type: UserType
    weekly_limit: int
    can_use_3d: bool
    can_see_prompts: bool
    
    class Config:
        from_attributes = True

# 用户状态信息
class UserStatus(BaseModel):
    user: UserResponse
    usage_this_week: int
    weekly_limit: int
    remaining_usage: int
    can_use_3d: bool
    can_see_prompts: bool
