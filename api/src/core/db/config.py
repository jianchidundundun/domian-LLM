from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, "data", "domains.db")

# 确保数据目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 获取数据库URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DB_PATH}"  # 默认使用SQLite
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 启用SQL语句日志
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建Base类
Base = declarative_base()

# FastAPI依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close() 