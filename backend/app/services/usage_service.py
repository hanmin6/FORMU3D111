from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.models.user import User, UserType, UsageLog, UserLimit
from app.schemas.user import UsageLogCreate, UserStatus

class UsageService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_limit(self, user_type: UserType) -> UserLimit:
        """获取用户类型对应的限制配置"""
        result = await self.db.execute(
            select(UserLimit).where(UserLimit.user_type == user_type)
        )
        user_limit = result.scalar_one_or_none()
        if not user_limit:
            # 如果数据库中没有配置，返回默认配置
            return UserLimit(
                user_type=user_type,
                weekly_limit=self._get_default_weekly_limit(user_type),
                can_use_3d=self._get_default_can_use_3d(user_type),
                can_see_prompts=self._get_default_can_see_prompts(user_type)
            )
        return user_limit
    
    def _get_default_weekly_limit(self, user_type: UserType) -> int:
        """获取默认周限制"""
        limits = {
            UserType.SPARK_PARTNER: 7,
            UserType.TIME_CURATOR: 100,
            UserType.FOUNDER: -1  # -1 表示无限制
        }
        return limits.get(user_type, 7)
    
    def _get_default_can_use_3d(self, user_type: UserType) -> bool:
        """获取默认3D使用权限"""
        return user_type == UserType.FOUNDER
    
    def _get_default_can_see_prompts(self, user_type: UserType) -> bool:
        """获取默认提示词查看权限"""
        return user_type != UserType.SPARK_PARTNER
    
    async def get_usage_this_week(self, user_id: int) -> int:
        """获取用户本周使用次数"""
        # 计算本周开始时间（周一）
        now = datetime.now()
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await self.db.execute(
            select(func.count(UsageLog.id)).where(
                and_(
                    UsageLog.user_id == user_id,
                    UsageLog.created_at >= week_start
                )
            )
        )
        return result.scalar() or 0
    
    async def can_use_feature(self, user: User, feature_type: str = "full_workflow") -> bool:
        """检查用户是否可以使用某个功能"""
        user_limit = await self.get_user_limit(user.user_type)
        
        # 创始人无限制
        if user.user_type == UserType.FOUNDER:
            return True
        
        # 检查3D功能权限
        if feature_type == "3d_generation" and not user_limit.can_use_3d:
            return False
        
        # 检查使用次数限制
        if user_limit.weekly_limit == -1:  # 无限制
            return True
        
        usage_this_week = await self.get_usage_this_week(user.id)
        return usage_this_week < user_limit.weekly_limit
    
    async def record_usage(self, user_id: int, usage_data: UsageLogCreate) -> UsageLog:
        """记录用户使用"""
        usage_log = UsageLog(
            user_id=user_id,
            workflow_type=usage_data.workflow_type,
            image_url=usage_data.image_url,
            result_url=usage_data.result_url
        )
        self.db.add(usage_log)
        await self.db.commit()
        await self.db.refresh(usage_log)
        return usage_log
    
    async def get_user_status(self, user: User) -> UserStatus:
        """获取用户状态信息"""
        user_limit = await self.get_user_limit(user.user_type)
        usage_this_week = await self.get_usage_this_week(user.id)
        
        remaining_usage = -1  # 无限制
        if user_limit.weekly_limit != -1:
            remaining_usage = max(0, user_limit.weekly_limit - usage_this_week)
        
        # 将User对象转换为UserResponse
        from app.schemas.user import UserResponse
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return UserStatus(
            user=user_response,
            usage_this_week=usage_this_week,
            weekly_limit=user_limit.weekly_limit,
            remaining_usage=remaining_usage,
            can_use_3d=user_limit.can_use_3d,
            can_see_prompts=user_limit.can_see_prompts
        )
    
    async def check_and_record_usage(self, user: User, feature_type: str = "full_workflow") -> bool:
        """检查权限并记录使用（如果允许）"""
        if not await self.can_use_feature(user, feature_type):
            return False
        
        # 记录使用（除了3D功能，因为3D功能是独立计费的）
        if feature_type != "3d_generation":
            await self.record_usage(
                user.id, 
                UsageLogCreate(workflow_type=feature_type)
            )
        
        return True

# 依赖注入函数
async def get_usage_service(db: AsyncSession) -> UsageService:
    return UsageService(db)
