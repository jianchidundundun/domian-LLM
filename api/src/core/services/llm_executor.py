from typing import List, Dict, Any, Optional
from src.core.rag.document_store import BaseDocumentStore
from src.core.llm_manager import LLMManager
from src.models.domain_models import Domain, ServiceEndpoint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import json
import logging
from ..execution.executor import PlanExecutor
from ..execution.models import ExecutionPlan, ExecutionStep
from src.adapter.adapter_manager import AdapterManager

logger = logging.getLogger(__name__)

def service_to_dict(service: ServiceEndpoint) -> dict:
    """将ServiceEndpoint对象转换为字典"""
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "endpoint_url": service.endpoint_url,
        "service_type": service.service_type,
        "methods": service.methods,
        "is_active": service.is_active
    }

class LLMExecutor:
    def __init__(
        self,
        document_store: BaseDocumentStore,
        llm_manager: LLMManager
    ):
        self.document_store = document_store
        self.llm_manager = llm_manager
        self.adapter_manager = AdapterManager()
        self.plan_executor = PlanExecutor(self.adapter_manager.connectors)
        
    async def execute_with_context(
        self,
        query: str,
        domain_name: str,
        db: AsyncSession,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行带上下文的查询"""
        try:
            # 获取域服务
            domain = await self._get_domain_services(domain_name, db)
            if not domain or not domain.services:
                raise ValueError(f"未找到领域 {domain_name} 的可用服务")
            
            # 将服务转换为字典格式
            services = [service_to_dict(service) for service in domain.services]
            
            # 生成执行计划
            plan_data = await self.llm_manager.generate_execution_plan(
                query=query,
                services=services,
                context=context
            )
            
            if not plan_data or "plan" not in plan_data:
                raise ValueError("生成的执行计划无效")
            
            # 创建执行计划对象
            execution_steps = []
            for step in plan_data["plan"]:
                execution_steps.append(
                    ExecutionStep(
                        service=step["service"],
                        method=step["method"],
                        parameters=step.get("parameters", {}),
                        description=step.get("description", "")
                    )
                )
            
            execution_plan = ExecutionPlan(plan=execution_steps)
            
            # 执行计划
            results = await self.plan_executor.execute_plan(execution_plan)
            
            return {
                "execution_plan": plan_data,
                "results": results.dict(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"执行失败: {str(e)}")
            raise ValueError(f"执行失败: {str(e)}")
            
    async def _get_domain_services(
        self,
        domain_name: str,
        db: AsyncSession
    ) -> Domain:
        """获取领域服务"""
        try:
            # 使用 selectinload 预加载服务关系
            stmt = (
                select(Domain)
                .where(Domain.name == domain_name)
                .options(selectinload(Domain.services))
            )
            result = await db.execute(stmt)
            domain = result.scalar_one_or_none()
            
            if domain is None:
                raise ValueError(f"未找到领域: {domain_name}")
                
            return domain
            
        except Exception as e:
            logger.error(f"获取领域服务失败: {str(e)}")
            raise
            
    async def _get_domain_services_old(
        self,
        domain_name: str,
        db: AsyncSession
    ) -> Domain:
        result = await db.execute(
            select(Domain)
            .where(Domain.name == domain_name)
            .join(Domain.services)
            .where(ServiceEndpoint.is_active == True)
        )
        return result.scalar_one_or_none() 