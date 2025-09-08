#!/usr/bin/env python3
"""
初始化数据库设置脚本
将环境变量中的配置迁移到数据库中
"""

import asyncio
import os
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.core.database import AsyncSessionLocal, ensure_database_and_tables
from app.services.setting_service import SettingService
from app.core.config import settings

async def init_settings():
    """初始化数据库设置"""
    
    # 确保数据库和表存在
    await ensure_database_and_tables()
    
    async with AsyncSessionLocal() as db:
        setting_service = SettingService(db)
        
        # 需要迁移的配置项
        config_mappings = {
            "COZE_BASE_URL": settings.COZE_BASE_URL,
            "COZE_AUTHORIZATION": settings.COZE_AUTHORIZATION,
            "PICTURE_ANALYSIS_BOT_ID": settings.PICTURE_ANALYSIS_BOT_ID,
            "CUTE_STYLE_PROMPT_GENERATION_BOT_ID": settings.CUTE_STYLE_PROMPT_GENERATION_BOT_ID,
            "STEAMPUNK_STYLE_PROMPT_GENERATION_BOT_ID": settings.STEAMPUNK_STYLE_PROMPT_GENERATION_BOT_ID,
            "JAPANESE_COMIC_STYLE_PROMPT_GENERATION_BOT_ID": settings.JAPANESE_COMIC_STYLE_PROMPT_GENERATION_BOT_ID,
            "AMERICAN_COMIC_STYLE_PROMPT_GENERATION_BOT_ID": settings.AMERICAN_COMIC_STYLE_PROMPT_GENERATION_BOT_ID,
            "PROFESSION_STYLE_PROMPT_GENERATION_BOT_ID": settings.PROFESSION_STYLE_PROMPT_GENERATION_BOT_ID,
            "CYBERPUNK_STYLE_PROMPT_GENERATION_BOT_ID": settings.CYBERPUNK_STYLE_PROMPT_GENERATION_BOT_ID,
            "GOTHIC_STYLE_PROMPT_GENERATION_BOT_ID": settings.GOTHIC_STYLE_PROMPT_GENERATION_BOT_ID,
            "REALISTIC_STYLE_PROMPT_GENERATION_BOT_ID": settings.REALISTIC_STYLE_PROMPT_GENERATION_BOT_ID,
            "TRIPO_API_KEY": settings.TRIPO_API_KEY,
            "SORA_BASE_URL": settings.SORA_BASE_URL,
            "SORA_API_KEY": settings.SORA_API_KEY,
        }
        
        print("开始初始化数据库设置...")
        
        for setting_name, setting_value in config_mappings.items():
            if setting_value:
                success = await setting_service.set_setting(
                    setting_name=setting_name,
                    setting_value=setting_value,
                    description=f"从环境变量迁移的 {setting_name} 配置"
                )
                if success:
                    print(f"✅ 设置 {setting_name} 成功")
                else:
                    print(f"❌ 设置 {setting_name} 失败")
            else:
                print(f"⚠️  跳过空值配置: {setting_name}")
        
        print("\n数据库设置初始化完成！")
        
        # 显示所有设置
        all_settings = await setting_service.get_all_settings()
        print(f"\n当前数据库中的设置数量: {len(all_settings)}")
        for name, value in all_settings.items():
            # 隐藏敏感信息
            display_value = value[:10] + "..." if len(value) > 10 and "KEY" in name or "AUTHORIZATION" in name else value
            print(f"  {name}: {display_value}")

if __name__ == "__main__":
    asyncio.run(init_settings())
