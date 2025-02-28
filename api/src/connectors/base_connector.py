from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Any:
        pass 