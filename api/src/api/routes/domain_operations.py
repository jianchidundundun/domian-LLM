from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.core.domain_manager import DomainManager
from pydantic import BaseModel

router = APIRouter()
domain_manager = DomainManager()

class OperationRequest(BaseModel):
    domain: str
    operation: str
    parameters: Dict[str, Any]

@router.post("/{domain}/{operation}")
async def execute_domain_operation(
    domain: str,
    operation: str,
    request: OperationRequest
):
    try:
        result = await domain_manager.execute_operation(
            domain,
            operation,
            request.parameters
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 