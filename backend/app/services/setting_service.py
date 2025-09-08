from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.models.setting import Setting
from app.core.logger import get_logger

logger = get_logger(__name__)

class SettingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_setting(self, setting_name: str) -> Optional[str]:
        """
        从数据库获取设置值
        """
        try:
            query = select(Setting).where(Setting.setting_name == setting_name)
            result = await self.db.execute(query)
            setting = result.scalar_one_or_none()
            
            if setting:
                logger.info(f"从数据库获取设置: {setting_name}")
                return setting.setting_value
            else:
                logger.warning(f"数据库中未找到设置: {setting_name}")
                return None
        except Exception as e:
            logger.error(f"获取设置失败 {setting_name}: {e}")
            return None

    async def set_setting(self, setting_name: str, setting_value: str, description: str = None) -> bool:
        """
        设置或更新数据库中的配置值
        """
        try:
            # 先查询是否存在
            query = select(Setting).where(Setting.setting_name == setting_name)
            result = await self.db.execute(query)
            existing_setting = result.scalar_one_or_none()
            
            if existing_setting:
                # 更新现有设置
                existing_setting.setting_value = setting_value
                if description:
                    existing_setting.description = description
                logger.info(f"更新设置: {setting_name}")
            else:
                # 创建新设置
                new_setting = Setting(
                    setting_name=setting_name,
                    setting_value=setting_value,
                    description=description
                )
                self.db.add(new_setting)
                logger.info(f"创建新设置: {setting_name}")
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"设置配置失败 {setting_name}: {e}")
            await self.db.rollback()
            return False

    async def get_all_settings(self) -> dict:
        """
        获取所有设置
        """
        try:
            query = select(Setting)
            result = await self.db.execute(query)
            settings = result.scalars().all()
            
            return {setting.setting_name: setting.setting_value for setting in settings}
        except Exception as e:
            logger.error(f"获取所有设置失败: {e}")
            return {}
