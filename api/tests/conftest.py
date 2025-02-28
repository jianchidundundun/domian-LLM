import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.db.config import get_db
from src.models.domain_models import Base
from src.mock_servers.matlab.server import matlab_app
import uvicorn
import multiprocessing
import time
from pytest_asyncio import fixture

# 使用SQLite内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

def start_mock_matlab_server():
    """启动模拟MATLAB服务器"""
    uvicorn.run(matlab_app, host="0.0.0.0", port=8001)

@pytest.fixture(scope="session", autouse=True)
def mock_servers():
    """启动所有模拟服务器"""
    # 启动MATLAB模拟服务器
    server_process = multiprocessing.Process(target=start_mock_matlab_server)
    server_process.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    yield
    
    # 清理
    server_process.terminate()
    server_process.join()

@fixture
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@fixture
async def test_db(test_engine):
    """创建测试数据库会话"""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        # 不需要在这里再次创建表，因为已经在 test_engine fixture 中创建了
        yield session
        # 回滚任何未提交的更改
        await session.rollback() 