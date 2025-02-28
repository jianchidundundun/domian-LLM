from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db.config import get_db
from src.core.services.llm_executor import LLMExecutor
from src.core.services.plan_executor import PlanExecutor
from src.core.rag.document_store import InMemoryDocumentStore
from src.core.llm_manager import LLMManager
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
document_store = InMemoryDocumentStore()
llm_manager = LLMManager()
llm_executor = LLMExecutor(document_store, llm_manager)
plan_executor = PlanExecutor()

class ExecutionRequest(BaseModel):
    query: str
    domain_name: str
    context: Optional[str] = None

class ExecutionResponse(BaseModel):
    execution_plan: Dict[str, Any]
    results: List[Dict[str, Any]]
    context: Optional[str] = None

@router.post("/execute", response_model=ExecutionResponse)
async def execute_with_context(
    request: ExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Generate execution plan
        execution_data = await llm_executor.execute_with_context(
            query=request.query,
            domain_name=request.domain_name,
            db=db,
            context=request.context if hasattr(request, 'context') else None
        )
        
        if "error" in execution_data and execution_data["error"]:
            raise HTTPException(
                status_code=500,
                detail=execution_data["error"]
            )
        
        return JSONResponse(
            content=execution_data,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        error_content = json.dumps({
            "detail": f"Execution failed: {str(e)}"
        }, ensure_ascii=False)
        return JSONResponse(
            status_code=500,
            content=json.loads(error_content),
            headers={"Content-Type": "application/json; charset=utf-8"}
        ) 