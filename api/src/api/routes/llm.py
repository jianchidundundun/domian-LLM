from fastapi import APIRouter, HTTPException
from src.api.models.request_models import QueryRequest, ChatRequest, TaskRequest
from src.core.llm_manager import LLMManager
from src.adapter.adapter_manager import AdapterManager
from typing import List, Dict, Any
import uuid

router = APIRouter()
llm_manager = LLMManager()
adapter_manager = AdapterManager()

@router.post("/query")
async def query(request: QueryRequest):
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        response = await llm_manager.process_query(
            request.query,
            session_id,
            domain=request.domain or "general",
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await llm_manager.chat(
            request.messages,
            request.context,
            provider=request.provider,
            model=request.model
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze(request: TaskRequest):
    try:
        result = await adapter_manager.execute_task(request.domain, request.task)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/ollama", response_model=List[str])
async def list_ollama_models():
    """Get available Ollama models list"""
    try:
        provider = llm_manager.providers.get("ollama")
        if not provider:
            raise HTTPException(status_code=404, detail="Ollama provider not configured")
        return await provider.list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 