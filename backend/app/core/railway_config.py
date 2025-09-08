"""
Railway 配置管理器
简化配置，直接从环境变量读取
"""

import os
from typing import Optional

class RailwayConfig:
    """Railway 配置管理器"""
    
    @staticmethod
    def get_coze_authorization() -> Optional[str]:
        """获取 Coze 授权令牌"""
        return os.getenv("COZE_AUTHORIZATION")
    
    @staticmethod
    def get_coze_base_url() -> Optional[str]:
        """获取 Coze 基础URL"""
        return os.getenv("COZE_BASE_URL")
    
    @staticmethod
    def get_sora_api_key() -> Optional[str]:
        """获取 Sora API 密钥"""
        return os.getenv("SORA_API_KEY")
    
    @staticmethod
    def get_sora_base_url() -> Optional[str]:
        """获取 Sora 基础URL"""
        return os.getenv("SORA_BASE_URL")
    
    @staticmethod
    def get_tripo_api_key() -> Optional[str]:
        """获取 Tripo API 密钥"""
        return os.getenv("TRIPO_API_KEY")
    
    @staticmethod
    def get_bot_id(bot_type: str) -> Optional[str]:
        """获取指定类型的 Bot ID"""
        return os.getenv(f"{bot_type.upper()}_BOT_ID")
    
    @staticmethod
    def get_database_url() -> str:
        """获取数据库连接字符串"""
        db_host = os.getenv("MYSQLHOST", "localhost")
        db_user = os.getenv("MYSQLUSER", "root")
        db_password = os.getenv("MYSQLPASSWORD", "")
        db_database = os.getenv("MYSQLDATABASE", "FORMU")
        db_port = int(os.getenv("MYSQLPORT", "3306"))
        
        # 调试信息
        print(f"Environment variables:")
        print(f"  MYSQLHOST: {db_host}")
        print(f"  MYSQLUSER: {db_user}")
        print(f"  MYSQLPASSWORD: {'***' if db_password else '(empty)'}")
        print(f"  MYSQLDATABASE: {db_database}")
        print(f"  MYSQLPORT: {db_port}")
        
        return f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
