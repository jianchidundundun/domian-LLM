from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class BaseDocumentStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        pass
    
    @abstractmethod
    async def delete_documents(self, filter: Dict[str, Any]) -> None:
        pass

class InMemoryDocumentStore(BaseDocumentStore):
    def __init__(self):
        self.documents: List[Document] = []
        
    async def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        # 简单实现，实际应该使用向量相似度搜索
        return self.documents[:top_k]
        
    async def delete_documents(self, filter: Dict[str, Any]) -> None:
        self.documents = [
            doc for doc in self.documents 
            if not all(doc.metadata.get(k) == v for k, v in filter.items())
        ] 