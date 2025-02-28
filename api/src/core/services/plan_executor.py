import aiohttp
from typing import Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)

class PlanExecutor:
    def __init__(self, connectors: Dict[str, Any] = None):
        self.connectors = connectors or {}
        
    async def execute_plan(
        self,
        plan: Dict[str, Any],
        services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        try:
            results = []
            steps = plan.get("plan", [])
            
            for step in steps:
                service_name = step.get("service")
                method = step.get("method")
                parameters = step.get("parameters", {})
                
                # 查找服务
                service = next(
                    (s for s in services if s["name"] == service_name),
                    None
                )
                
                if not service:
                    raise ValueError(f"找不到服务: {service_name}")
                
                # 验证方法
                if method not in service.get("methods", {}):
                    raise ValueError(f"服务 {service_name} 不支持方法: {method}")
                
                # 调用服务
                try:
                    connector = self.connectors.get(service["service_type"])
                    if not connector:
                        raise ValueError(f"找不到服务类型的连接器: {service['service_type']}")
                        
                    response = await connector.call_method(
                        service["endpoint_url"],
                        method,
                        parameters
                    )
                    
                    result = {
                        "step": step.get("description", ""),
                        "status": "success",
                        "result": response
                    }
                except Exception as e:
                    logger.error(f"步骤执行失败: {str(e)}")
                    result = {
                        "step": step.get("description", ""),
                        "status": "error",
                        "error": str(e)
                    }
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"执行计划失败: {str(e)}")
            raise ValueError(f"执行计划失败: {str(e)}") 