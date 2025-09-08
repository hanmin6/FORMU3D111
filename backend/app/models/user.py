from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserType(str, enum.Enum):
    SPARK_PARTNER = "spark_partner"  # 星火合伙人
    TIME_CURATOR = "time_curator"    # 时光主理人
    FOUNDER = "founder"              # 创始人

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), default=UserType.SPARK_PARTNER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    workflow_type = Column(String(50), nullable=False)  # "full_workflow", "sora_only", "3d_generation"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联信息
    image_url = Column(String(500))  # 上传的图片URL
    result_url = Column(String(500))  # 生成结果的URL

class UserLimit(Base):
    __tablename__ = "user_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(Enum(UserType), unique=True, nullable=False)
    weekly_limit = Column(Integer, nullable=False)
    can_use_3d = Column(Boolean, default=False, nullable=False)
    can_see_prompts = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
