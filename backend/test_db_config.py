#!/usr/bin/env python3
"""
测试数据库配置
"""

import os
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent
sys.path.append(str(project_root))

from app.core.config import settings

def test_database_config():
    """测试数据库配置"""
    print("🔍 检查数据库配置...")
    print()
    
    # 显示环境变量
    print("📋 Railway 环境变量:")
    railway_vars = ["MYSQLHOST", "MYSQLUSER", "MYSQLPASSWORD", "MYSQLDATABASE", "MYSQLPORT"]
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            # 隐藏密码
            display_value = "***" if "PASSWORD" in var else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    print()
    print("📋 配置类中的默认值:")
    print(f"  DB_HOST: {settings.DB_HOST}")
    print(f"  DB_USER: {settings.DB_USER}")
    print(f"  DB_PASSWORD: {'***' if settings.DB_PASSWORD else '(空)'}")
    print(f"  DB_NAME: {settings.DB_NAME}")
    print(f"  DB_PORT: {settings.DB_PORT}")
    
    print()
    print("🔗 最终数据库连接字符串:")
    db_url = settings.DATABASE_URL
    # 隐藏密码
    safe_url = db_url.split('@')[0].split(':')[0] + ':***@' + '@'.join(db_url.split('@')[1:])
    print(f"  {safe_url}")
    
    print()
    print("✅ 数据库配置检查完成！")

if __name__ == "__main__":
    test_database_config()
