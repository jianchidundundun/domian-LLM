from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ExecutionStep(BaseModel):
    """单个执行步骤的模型"""
    service: str  # 服务名称（如 'matlab'）
    method: str   # 方法名称
    parameters: Dict[str, Any]  # 方法参数
    description: str  # 步骤描述
    
class ExecutionPlan(BaseModel):
    """完整执行计划的模型"""
    plan: List[ExecutionStep]
    context: Optional[Dict[str, Any]] = None
    
class StepResult(BaseModel):
    """单个步骤的执行结果"""
    step: ExecutionStep
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    
class ExecutionResult(BaseModel):
    """完整执行结果"""
    success: bool
    results: List[StepResult]
    error: Optional[str] = None 