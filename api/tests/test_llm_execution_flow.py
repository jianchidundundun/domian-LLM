import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.services.llm_executor import LLMExecutor
from src.core.llm_manager import LLMManager
from src.core.rag.faiss_document_store import FAISSDocumentStore
from src.models.domain_models import Domain, ServiceEndpoint
from datetime import datetime
from pytest_asyncio import fixture
from sqlalchemy import delete
import aiohttp
import logging
import json
import os
from pathlib import Path

# 创建日志目录
log_dir = Path("tests/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'test.log')
    ]
)
logger = logging.getLogger(__name__)

def service_to_dict(service: ServiceEndpoint) -> dict:
    """将ServiceEndpoint对象转换为字典"""
    return {
        "id": service.id,
        "domain_id": service.domain_id,
        "name": service.name,
        "description": service.description,
        "endpoint_url": service.endpoint_url,
        "service_type": service.service_type,
        "methods": service.methods,
        "is_active": service.is_active
    }

async def check_matlab_server():
    """检查MATLAB服务器是否运行"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8001/health") as response:
                logger.info(f"MATLAB服务器健康检查响应: {response.status}")
                return response.status == 200
        except aiohttp.ClientError as e:
            logger.error(f"MATLAB服务器连接失败: {str(e)}")
            return False

@pytest.mark.asyncio
async def test_llm_execution_flow(test_db: AsyncSession):
    """测试完整的LLM执行流程"""
    logger.info("开始执行LLM执行流程测试")
    
    # 确保服务器在运行
    server_status = await check_matlab_server()
    logger.info(f"MATLAB服务器状态: {'运行中' if server_status else '未运行'}")
    assert server_status, "MATLAB mock server is not running"
    
    try:
        # 1. 设置测试环境
        logger.info("初始化测试环境...")
        document_store = FAISSDocumentStore(
            embedding_model="paraphrase-MiniLM-L3-v2",
            dimension=384,
            index_type="l2"
        )
        
        llm_manager = LLMManager()
        executor = LLMExecutor(document_store, llm_manager)
        
        # 2. 创建测试数据
        logger.info("创建测试领域...")
        domain = Domain(
            name="信号处理",
            description="信号处理相关服务"
        )
        test_db.add(domain)
        await test_db.flush()
        logger.info(f"领域创建成功，ID: {domain.id}")
        
        # 修改服务注册方式，确保数据可以序列化
        service_data = {
            "domain_id": domain.id,
            "name": "matlab",
            "description": "MATLAB信号处理服务",
            "endpoint_url": "http://localhost:8001",
            "service_type": "matlab",
            "methods": {
                "filter": {
                    "description": "应用数字滤波器",
                    "parameters": {
                        "x": "输入信号",
                        "b": "滤波器系数b",
                        "a": "滤波器系数a"
                    }
                },
                "fft": {
                    "description": "计算快速傅里叶变换",
                    "parameters": {
                        "data": "输入数据"
                    }
                }
            },
            "is_active": True
        }
        
        logger.info("创建服务端点...")
        logger.debug(f"服务数据: {json.dumps(service_data, indent=2)}")
        
        matlab_service = ServiceEndpoint(**service_data)
        test_db.add(matlab_service)
        await test_db.commit()
        
        # 记录服务信息
        service_dict = service_to_dict(matlab_service)
        logger.info(f"服务端点创建成功: {json.dumps(service_dict, indent=2)}")
        
        # 3. 执行测试查询
        test_query = "对信号 [1,2,3,4,5] 进行低通滤波"
        logger.info(f"执行测试查询: {test_query}")
        
        result = await executor.execute_with_context(
            query=test_query,
            domain_name="信号处理",
            db=test_db
        )
        logger.info(f"执行结果: {json.dumps(result, indent=2)}")
        
        assert result is not None
        assert "execution_plan" in result
        assert "results" in result
            
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}")
        raise
    finally:
        # 清理测试数据
        try:
            await test_db.rollback()  # 确保没有未完成的事务
            await test_db.execute(delete(ServiceEndpoint).where(ServiceEndpoint.domain_id == domain.id))
            await test_db.execute(delete(Domain).where(Domain.id == domain.id))
            await test_db.commit()
            logger.info("测试数据清理完成")
        except Exception as e:
            logger.error(f"清理测试数据失败: {str(e)}")
            await test_db.rollback()

@pytest.mark.asyncio
async def test_error_cases(test_db: AsyncSession):
    """测试错误处理"""
    logger.info("开始执行错误处理测试")
    
    # 设置测试环境
    document_store = FAISSDocumentStore(
        embedding_model="paraphrase-MiniLM-L3-v2",
        dimension=384,
        index_type="l2"
    )
    llm_manager = LLMManager()
    executor = LLMExecutor(document_store, llm_manager)
    
    # 测试查询不存在的领域
    logger.info("测试查询不存在的领域...")
    result = await executor.execute_with_context(
        query="测试查询",
        domain_name="不存在的领域",
        db=test_db
    )
    
    assert result["success"] is False
    assert "找不到领域" in result["error"]
    
    logger.info("错误处理测试完成") 