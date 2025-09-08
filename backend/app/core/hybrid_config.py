"""
混合配置管理器
优先从数据库读取配置，如果数据库中没有则使用环境变量作为后备
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.services.setting_service import SettingService
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class HybridConfig:
    """混合配置管理器：数据库优先，环境变量后备"""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 缓存5分钟
    
    async def get_setting(self, setting_name: str, env_fallback: str = None) -> Optional[str]:
        """
        获取设置值：优先从数据库，后备环境变量
        
        Args:
            setting_name: 设置名称
            env_fallback: 环境变量后备值
            
        Returns:
            设置值或None
        """
        try:
            # 检查缓存
            if setting_name in self._cache:
                return self._cache[setting_name]
            
            # 从数据库获取
            async with AsyncSessionLocal() as db:
                setting_service = SettingService(db)
                db_value = await setting_service.get_setting(setting_name)
                
                if db_value:
                    # 数据库中有值，使用数据库值
                    self._cache[setting_name] = db_value
                    logger.info(f"从数据库获取配置: {setting_name}")
                    return db_value
                else:
                    # 数据库中没有，使用环境变量后备
                    if env_fallback:
                        logger.info(f"数据库中没有 {setting_name}，使用环境变量后备")
                        self._cache[setting_name] = env_fallback
                        return env_fallback
                    else:
                        logger.warning(f"数据库和环境变量中都没有找到: {setting_name}")
                        return None
                        
        except Exception as e:
            logger.error(f"获取配置失败 {setting_name}: {e}")
            # 出错时使用环境变量后备
            if env_fallback:
                logger.info(f"出错时使用环境变量后备: {setting_name}")
                return env_fallback
            return None
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("配置缓存已清除")

# 全局配置实例
hybrid_config = HybridConfig()

# 便捷函数
async def get_coze_authorization() -> Optional[str]:
    """获取 Coze 授权令牌"""
    return await hybrid_config.get_setting("COZE_AUTHORIZATION", settings.COZE_AUTHORIZATION)

async def get_coze_base_url() -> Optional[str]:
    """获取 Coze 基础URL"""
    return await hybrid_config.get_setting("COZE_BASE_URL", settings.COZE_BASE_URL)

async def get_sora_api_key() -> Optional[str]:
    """获取 Sora API 密钥"""
    return await hybrid_config.get_setting("SORA_API_KEY", settings.SORA_API_KEY)

async def get_sora_base_url() -> Optional[str]:
    """获取 Sora 基础URL"""
    return await hybrid_config.get_setting("SORA_BASE_URL", settings.SORA_BASE_URL)

async def get_tripo_api_key() -> Optional[str]:
    """获取 Tripo API 密钥"""
    return await hybrid_config.get_setting("TRIPO_API_KEY", settings.TRIPO_API_KEY)

async def get_bot_id(bot_type: str) -> Optional[str]:
    """获取指定类型的 Bot ID"""
    env_attr = f"{bot_type.upper()}_BOT_ID"
    env_value = getattr(settings, env_attr, None)
    return await hybrid_config.get_setting(env_attr, env_value)
