import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.core.railway_config import RailwayConfig

# 设置 SQLAlchemy 日志级别为 WARNING，这样就不会显示 INFO 级别的 SQL 查询日志
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# 全局变量，延迟初始化
engine = None
AsyncSessionLocal = None

def get_engine():
    """获取数据库引擎，延迟初始化"""
    global engine
    if engine is None:
        db_url = RailwayConfig.get_database_url()
        print(f"Creating database engine with URL: {db_url[:50]}...")  # 只显示前50个字符
        engine = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return engine

def get_session_local():
    """获取会话工厂，延迟初始化"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return AsyncSessionLocal

# 创建基类
Base = declarative_base()

# 获取数据库会话的依赖函数
async def get_db():
    session_local = get_session_local()
    async with session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 


async def ensure_database_and_tables():
    """
    确保目标数据库存在，并在启动时创建缺失的数据表。
    1) 连接到服务器级别（不指定数据库），执行 CREATE DATABASE IF NOT EXISTS
    2) 使用目标数据库的 engine 创建所有表
    """
    # 1) 连接到服务器级别
    db_url = RailwayConfig.get_database_url()
    print(f"Database URL: {db_url[:50]}...")  # 只显示前50个字符
    
    # 从完整URL中提取服务器URL（去掉数据库名）
    server_url = '/'.join(db_url.split('/')[:-1]) + '/'
    print(f"Server URL: {server_url[:50]}...")
    
    server_engine = create_async_engine(server_url, echo=False, pool_pre_ping=True)
    try:
        async with server_engine.begin() as conn:
            # 从环境变量获取数据库名
            import os
            db_name = os.getenv("MYSQLDATABASE", "FORMU")
            await conn.execute(text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ))
    finally:
        await server_engine.dispose()

    # 2) 确保模型已导入，从而 Base.metadata 包含所有表
    # 仅导入一次，避免循环依赖
    from app.models import setting as setting_model  # noqa: F401
    from app.models import user as user_model  # noqa: F401

    # 3) 在目标数据库中创建表（如不存在）
    db_engine = get_engine()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)