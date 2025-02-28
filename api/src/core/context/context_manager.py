from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

class Context(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]
    history: List[Dict[str, Any]]

class ContextManager:
    def __init__(self):
        self.contexts: Dict[str, Context] = {}
    
    def create_context(self, session_id: str) -> Context:
        now = datetime.now()
        context = Context(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            data={},
            history=[]
        )
        self.contexts[session_id] = context
        return context
    
    def get_context(self, session_id: str) -> Optional[Context]:
        return self.contexts.get(session_id)
    
    def update_context(
        self, 
        session_id: str, 
        data: Dict[str, Any], 
        message: Dict[str, Any]
    ) -> None:
        context = self.get_context(session_id)
        if not context:
            context = self.create_context(session_id)
        
        context.data.update(data)
        context.history.append(message)
        context.updated_at = datetime.now() 