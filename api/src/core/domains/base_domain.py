from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from abc import ABC, abstractmethod

class DomainOperation(BaseModel):
    """领域操作的基类"""
    operation_id: str
    description: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]

class DomainKnowledge(BaseModel):
    """领域知识的基类"""
    concepts: List[str]
    documents: List[str]
    operations: List[DomainOperation]

class BaseDomain(ABC):
    """领域适配器的基类"""
    def __init__(self, name: str):
        self.name = name
        self._operations: Dict[str, DomainOperation] = {}
        self._knowledge: Optional[DomainKnowledge] = None
        
    @abstractmethod
    def load_knowledge(self) -> DomainKnowledge:
        """加载领域知识"""
        pass
        
    @abstractmethod
    def get_prompt_templates(self) -> Dict[str, str]:
        """获取领域特定的提示词模板"""
        pass
        
    def register_operation(self, operation: DomainOperation) -> None:
        """注册领域操作"""
        self._operations[operation.operation_id] = operation
        
    def get_operation(self, operation_id: str) -> Optional[DomainOperation]:
        """获取领域操作"""
        return self._operations.get(operation_id) 