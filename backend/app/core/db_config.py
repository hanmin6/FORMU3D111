from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.services.setting_service import SettingService
from app.core.database import AsyncSessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)

class DatabaseConfig:
    """从数据库获取配置的类"""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 缓存5分钟
    
    async def get_setting(self, setting_name: str, default_value: str = None) -> Optional[str]:
        """
        从数据库获取设置值，带缓存
        """
        try:
            # 检查缓存
            if setting_name in self._cache:
                return self._cache[setting_name]
            
            # 从数据库获取
            async with AsyncSessionLocal() as db:
                setting_service = SettingService(db)
                value = await setting_service.get_setting(setting_name)
                
                if value:
                    # 缓存结果
                    self._cache[setting_name] = value
                    logger.info(f"从数据库获取配置: {setting_name}")
                    return value
                else:
                    logger.warning(f"数据库中未找到配置: {setting_name}，使用默认值: {default_value}")
                    return default_value
                    
        except Exception as e:
            logger.error(f"获取配置失败 {setting_name}: {e}")
            return default_value
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("配置缓存已清除")

# 全局配置实例
db_config = DatabaseConfig()

# 便捷函数
async def get_coze_authorization() -> Optional[str]:
    """获取 Coze 授权令牌"""
    return await db_config.get_setting("COZE_AUTHORIZATION")

async def get_coze_base_url() -> Optional[str]:
    """获取 Coze 基础URL"""
    return await db_config.get_setting("COZE_BASE_URL")

async def get_sora_api_key() -> Optional[str]:
    """获取 Sora API 密钥"""
    return await db_config.get_setting("SORA_API_KEY")

async def get_sora_base_url() -> Optional[str]:
    """获取 Sora 基础URL"""
    return await db_config.get_setting("SORA_BASE_URL")

async def get_tripo_api_key() -> Optional[str]:
    """获取 Tripo API 密钥"""
    return await db_config.get_setting("TRIPO_API_KEY")

async def get_bot_id(bot_type: str) -> Optional[str]:
    """获取指定类型的 Bot ID"""
    return await db_config.get_setting(f"{bot_type.upper()}_BOT_ID")
