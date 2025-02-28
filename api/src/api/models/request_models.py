from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class QueryRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    context: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None

class TaskRequest(BaseModel):
    domain: str
    task: Dict[str, Any]

class ExecutionRequest(BaseModel):
    query: str
    context: Optional[str] = None 