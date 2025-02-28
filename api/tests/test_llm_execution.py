import pytest
from httpx import AsyncClient
from src.main import app
from src.core.db.config import get_db
from src.models.domain_models import Domain, ServiceEndpoint, Document
from sqlalchemy.ext.asyncio import AsyncSession
import json

@pytest.mark.asyncio
async def test_llm_execution_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 创建测试领域
        domain_response = await client.post(
            "/api/v1/domains",
            json={
                "name": "信号处理测试",
                "description": "用于单元测试的信号处理领域"
            }
        )
        assert domain_response.status_code == 200
        domain_id = domain_response.json()["domain_id"]
        
        # 2. 注册测试服务
        service_response = await client.post(
            "/api/v1/services/register",
            json={
                "domain_name": "信号处理测试",
                "service_name": "test_filters",
                "description": "测试用滤波器服务",
                "endpoint_url": "http://localhost:8001",
                "service_type": "matlab",
                "methods": {
                    "lowpass": {
                        "parameters": {
                            "signal": "array",
                            "cutoff_freq": "float",
                            "sampling_rate": "float"
                        }
                    }
                }
            }
        )
        assert service_response.status_code == 200
        
        # 3. 创建测试文档
        doc_content = """
        低通滤波器用于去除信号中的高频噪声。
        使用时需要设置截止频率和采样率。
        截止频率决定了滤波器的截止点。
        """
        
        # 获取数据库会话
        async for db in get_db():
            # 直接创建测试文档
            doc = Document(
                domain_id=domain_id,
                filename="test_doc.txt",
                content=doc_content
            )
            db.add(doc)
            await db.commit()
            
        # 4. 测试LLM执行
        execution_response = await client.post(
            "/api/v1/llm/execute",
            json={
                "query": "如何使用低通滤波器处理信号？",
                "domain_name": "信号处理测试"
            }
        )
        assert execution_response.status_code == 200
        
        result = execution_response.json()
        assert "execution_plan" in result
        assert "results" in result
        assert "context" in result
        
        # 验证执行计划格式
        plan = result["execution_plan"]
        assert "plan" in plan
        assert isinstance(plan["plan"], list)
        assert len(plan["plan"]) > 0
        assert "explanation" in plan
        
        # 验证第一个步骤
        first_step = plan["plan"][0]
        assert "service" in first_step
        assert "method" in first_step
        assert "parameters" in first_step
        assert "description" in first_step
        
        # 清理测试数据
        async for db in get_db():
            await db.execute(f"DELETE FROM documents WHERE domain_id = {domain_id}")
            await db.execute(f"DELETE FROM service_endpoints WHERE domain_id = {domain_id}")
            await db.execute(f"DELETE FROM domains WHERE id = {domain_id}")
            await db.commit()

@pytest.mark.asyncio
async def test_error_handling():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 测试不存在的领域
        response = await client.post(
            "/api/v1/llm/execute",
            json={
                "query": "测试查询",
                "domain_name": "不存在的领域"
            }
        )
        assert response.status_code == 500
        assert "未找到领域" in response.json()["detail"]
        
        # 测试空查询
        response = await client.post(
            "/api/v1/llm/execute",
            json={
                "query": "",
                "domain_name": "信号处理"
            }
        )
        assert response.status_code == 422  # FastAPI的验证错误

if __name__ == "__main__":
    pytest.main(["-v", "test_llm_execution.py"]) 