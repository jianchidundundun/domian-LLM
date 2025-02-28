from .base_domain import BaseDomain, DomainOperation, DomainKnowledge
from typing import Dict, Any, List

class SignalProcessingDomain(BaseDomain):
    def __init__(self):
        super().__init__("signal_processing")
        self._register_default_operations()
        
    def load_knowledge(self) -> DomainKnowledge:
        return DomainKnowledge(
            concepts=[
                "数字滤波器",
                "频率响应",
                "信号采样",
                # ...其他概念
            ],
            documents=[
                "signal_processing/filter_concepts.txt",
                "signal_processing/filter_examples.txt",
                # ...其他文档
            ],
            operations=list(self._operations.values())
        )
        
    def get_prompt_templates(self) -> Dict[str, str]:
        return {
            "analysis": """你是一个信号处理专家。基于上下文：
{context}
分析问题：{query}
可用的操作：{available_operations}
""",
            "operation": """请针对以下操作提供具体建议：
操作：{operation}
输入：{input}
期望输出：{expected_output}
"""
        }
        
    def _register_default_operations(self) -> None:
        # 注册滤波器操作
        self.register_operation(DomainOperation(
            operation_id="filter",
            description="应用数字滤波器到信号",
            parameters={
                "data": "List[float]",
                "filter_type": "str",
                "parameters": "Optional[Dict[str, Any]]"
            },
            examples=[{
                "data": [1.0, 2.0, 3.0],
                "filter_type": "moving_average",
                "parameters": {"window_size": 3}
            }]
        ))
        # 可以注册更多信号处理操作... 