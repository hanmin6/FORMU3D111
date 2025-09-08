from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.core.database import get_db
from app.services.setting_service import SettingService
from app.core.railway_config import RailwayConfig

router = APIRouter()

@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """获取所有设置"""
    try:
        setting_service = SettingService(db)
        all_settings = await setting_service.get_all_settings()
        
        # 返回格式化的设置
        formatted_settings = {
            "cozeAuthorization": all_settings.get("COZE_AUTHORIZATION", ""),
            "cozeBaseUrl": all_settings.get("COZE_BASE_URL", ""),
            "pictureAnalysisBotId": all_settings.get("PICTURE_ANALYSIS_BOT_ID", ""),
            "cuteStyleBotId": all_settings.get("CUTE_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "steampunkStyleBotId": all_settings.get("STEAMPUNK_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "japaneseComicStyleBotId": all_settings.get("JAPANESE_COMIC_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "americanComicStyleBotId": all_settings.get("AMERICAN_COMIC_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "professionStyleBotId": all_settings.get("PROFESSION_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "cyberpunkStyleBotId": all_settings.get("CYBERPUNK_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "gothicStyleBotId": all_settings.get("GOTHIC_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "realisticStyleBotId": all_settings.get("REALISTIC_STYLE_PROMPT_GENERATION_BOT_ID", ""),
            "soraApiKey": all_settings.get("SORA_API_KEY", ""),
            "soraBaseUrl": all_settings.get("SORA_BASE_URL", ""),
            "tripoApiKey": all_settings.get("TRIPO_API_KEY", ""),
        }
        
        return formatted_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@router.post("/settings")
async def save_settings(settings: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """保存设置"""
    try:
        setting_service = SettingService(db)
        
        # 设置映射
        setting_mappings = {
            "cozeAuthorization": "COZE_AUTHORIZATION",
            "cozeBaseUrl": "COZE_BASE_URL",
            "pictureAnalysisBotId": "PICTURE_ANALYSIS_BOT_ID",
            "cuteStyleBotId": "CUTE_STYLE_PROMPT_GENERATION_BOT_ID",
            "steampunkStyleBotId": "STEAMPUNK_STYLE_PROMPT_GENERATION_BOT_ID",
            "japaneseComicStyleBotId": "JAPANESE_COMIC_STYLE_PROMPT_GENERATION_BOT_ID",
            "americanComicStyleBotId": "AMERICAN_COMIC_STYLE_PROMPT_GENERATION_BOT_ID",
            "professionStyleBotId": "PROFESSION_STYLE_PROMPT_GENERATION_BOT_ID",
            "cyberpunkStyleBotId": "CYBERPUNK_STYLE_PROMPT_GENERATION_BOT_ID",
            "gothicStyleBotId": "GOTHIC_STYLE_PROMPT_GENERATION_BOT_ID",
            "realisticStyleBotId": "REALISTIC_STYLE_PROMPT_GENERATION_BOT_ID",
            "soraApiKey": "SORA_API_KEY",
            "soraBaseUrl": "SORA_BASE_URL",
            "tripoApiKey": "TRIPO_API_KEY",
        }
        
        # 保存每个设置
        for frontend_key, backend_key in setting_mappings.items():
            value = settings.get(frontend_key, "")
            if value:  # 只保存非空值
                await setting_service.set_setting(
                    setting_name=backend_key,
                    setting_value=value,
                    description=f"通过前端设置界面配置的 {backend_key}"
                )
        
        # 设置已保存到数据库
        
        return {"message": "设置保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存设置失败: {str(e)}")
