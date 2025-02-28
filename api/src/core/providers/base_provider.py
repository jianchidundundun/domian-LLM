from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Union

T = TypeVar('T')

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        pass 