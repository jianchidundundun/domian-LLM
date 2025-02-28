from typing import Dict, Any, List, Optional
from .models import ExecutionPlan, ExecutionStep, StepResult, ExecutionResult
from src.connectors.base_connector import BaseConnector
import logging
import asyncio

logger = logging.getLogger(__name__)

class PlanExecutor:
    def __init__(self, connectors: Dict[str, BaseConnector]):
        """
        初始化执行器
        Args:
            connectors: 服务连接器字典，key为服务名称，value为对应的连接器实例
        """
        self.connectors = connectors
        
    async def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """执行计划"""
        results = []
        previous_results = {}
        success = True
        error = None
        
        try:
            for step in plan.plan:
                # 执行单个步骤
                step_result = await self._execute_step(step, previous_results)
                results.append(step_result)
                
                # 如果步骤失败，标记整个执行为失败
                if not step_result.success:
                    success = False
                    error = step_result.error
                    break
                    
                # 存储结果供后续步骤使用
                if step_result.success and step_result.result is not None:
                    previous_results[f"{step.service}.{step.method}"] = step_result.result
                    
            return ExecutionResult(
                success=success,
                results=results,
                error=error
            )
            
        except Exception as e:
            logger.error(f"计划执行失败: {str(e)}")
            return ExecutionResult(
                success=False,
                results=results,
                error=str(e)
            )
    
    async def _execute_step(
        self, 
        step: ExecutionStep,
        previous_results: Dict[str, Any]
    ) -> StepResult:
        """执行单个步骤"""
        try:
            # 获取连接器
            connector = self.connectors.get(step.service)
            if not connector:
                raise ValueError(f"未找到服务 {step.service} 的连接器")
            
            # 准备参数
            parameters = self._prepare_parameters(step.parameters, previous_results)
            
            # 执行任务
            result = await connector.execute({
                "function": step.method,
                "args": [],
                "kwargs": parameters
            })
            
            return StepResult(
                step=step,
                success=True,
                result=result
            )
            
        except Exception as e:
            logger.error(f"步骤执行失败: {str(e)}")
            return StepResult(
                step=step,
                success=False,
                error=str(e)
            )
    
    def _prepare_parameters(
        self,
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理参数中的引用，支持使用前面步骤的结果
        Args:
            parameters: 原始参数
            previous_results: 之前步骤的结果
        Returns:
            处理后的参数
        """
        processed_params = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("$ref:"):
                # 处理引用格式：$ref:service.method.field
                ref_path = value[5:].split(".")
                ref_result = previous_results.get(f"{ref_path[0]}.{ref_path[1]}")
                if ref_result is None:
                    raise ValueError(f"Referenced result not found: {value}")
                if len(ref_path) > 2:
                    for field in ref_path[2:]:
                        ref_result = ref_result.get(field)
                processed_params[key] = ref_result
            else:
                processed_params[key] = value
                
        return processed_params 