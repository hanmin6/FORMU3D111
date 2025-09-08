#!/usr/bin/env python3
"""
初始化用户限制配置脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))

from app.core.database import get_engine
from app.models.user import UserLimit, UserType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def init_user_limits():
    """初始化用户限制配置"""
    engine = get_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 检查是否已经存在配置
        from sqlalchemy import select
        result = await session.execute(select(UserLimit))
        existing_limits = result.scalars().all()
        
        if existing_limits:
            print("用户限制配置已存在，跳过初始化")
            return
        
        # 创建默认配置
        limits = [
            UserLimit(
                user_type=UserType.SPARK_PARTNER,
                weekly_limit=7,
                can_use_3d=False,
                can_see_prompts=False
            ),
            UserLimit(
                user_type=UserType.TIME_CURATOR,
                weekly_limit=100,
                can_use_3d=False,
                can_see_prompts=True
            ),
            UserLimit(
                user_type=UserType.FOUNDER,
                weekly_limit=-1,  # 无限制
                can_use_3d=True,
                can_see_prompts=True
            )
        ]
        
        for limit in limits:
            session.add(limit)
        
        await session.commit()
        print("用户限制配置初始化完成")
        
        # 显示配置
        for limit in limits:
            print(f"- {limit.user_type.value}: 周限制={limit.weekly_limit}, 3D权限={limit.can_use_3d}, 提示词权限={limit.can_see_prompts}")

if __name__ == "__main__":
    asyncio.run(init_user_limits())
