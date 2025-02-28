import pytest
from src.core.execution.executor import PlanExecutor
from src.core.execution.models import ExecutionPlan, ExecutionStep
from src.connectors.matlab.matlab_connector import MatlabConnector

@pytest.mark.asyncio
async def test_simple_plan_execution():
    """测试简单的执行计划"""
    # 创建测试连接器
    connectors = {
        "matlab": MatlabConnector()
    }
    
    # 创建执行器
    executor = PlanExecutor(connectors)
    
    # 创建测试计划
    plan = ExecutionPlan(
        plan=[
            ExecutionStep(
                service="matlab",
                method="filter",
                parameters={
                    "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                    "b": [0.2, 0.2, 0.2, 0.2, 0.2],
                    "a": [1.0]
                },
                description="应用低通滤波器"
            )
        ]
    )
    
    # 执行计划
    result = await executor.execute_plan(plan)
    
    # 验证结果
    assert result.success
    assert len(result.results) == 1
    assert result.results[0].success
    assert isinstance(result.results[0].result, list)

@pytest.mark.asyncio
async def test_multi_step_plan_execution():
    """测试多步骤执行计划"""
    connectors = {
        "matlab": MatlabConnector()
    }
    
    executor = PlanExecutor(connectors)
    
    # 创建多步骤计划
    plan = ExecutionPlan(
        plan=[
            ExecutionStep(
                service="matlab",
                method="filter",
                parameters={
                    "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                    "b": [0.2, 0.2, 0.2, 0.2, 0.2],
                    "a": [1.0]
                },
                description="应用低通滤波器"
            ),
            ExecutionStep(
                service="matlab",
                method="fft",
                parameters={
                    "data": "$ref:matlab.filter"
                },
                description="计算频谱"
            )
        ]
    )
    
    result = await executor.execute_plan(plan)
    
    # 验证结果
    assert result.success
    assert len(result.results) == 2
    assert all(r.success for r in result.results)
    assert isinstance(result.results[0].result, list)
    assert isinstance(result.results[1].result, list)

@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    connectors = {
        "matlab": MatlabConnector()
    }
    
    executor = PlanExecutor(connectors)
    
    # 创建一个会失败的计划
    plan = ExecutionPlan(
        plan=[
            ExecutionStep(
                service="unknown_service",
                method="unknown_method",
                parameters={},
                description="这个步骤会失败"
            )
        ]
    )
    
    result = await executor.execute_plan(plan)
    
    # 验证错误处理
    assert not result.success
    assert result.error is not None
    assert "Service unknown_service not found" in result.error 