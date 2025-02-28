from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import llm, signal_processing, domain_config, service_registry, llm_execution
from src.core.rag.utils import load_documents
import uvicorn
from typing import Any
import os
from .core.db.domain_db import DomainDB
from pathlib import Path
from fastapi.responses import JSONResponse
import time
import asyncio
import logging
from src.core.llm_manager import LLMManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Domain Framework",
    description="Professional Domain LLM Framework API",
    version="0.1.0"
)

# Modify CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(llm.router, prefix="/api/v1", tags=["LLM"])
app.include_router(signal_processing.router, prefix="/api/v1/signal", tags=["Signal Processing"])
app.include_router(domain_config.router, prefix="/api/v1", tags=["Domain Configuration"])
app.include_router(service_registry.router, prefix="/api/v1", tags=["Service Registry"])
app.include_router(llm_execution.router, prefix="/api/v1/llm", tags=["LLM Execution"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and load documents on startup"""
    try:
        # Initialize database
        await DomainDB.init_db()
        logger.info("Database initialization completed")
        
        # Load documents
        docs_dir = os.path.join(Path(__file__).parent.parent, "data", "documents")
        if os.path.exists(docs_dir):
            logger.info(f"Loading documents from {docs_dir}...")
            # TODO: Implement document loading logic
    except Exception as e:
        logger.error(f"Startup initialization failed: {str(e)}")

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Request timeout middleware"""
    try:
        # Increase timeout to 120 seconds
        return await asyncio.wait_for(call_next(request), timeout=120.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout, please try again later"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Request logging middleware"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} Processing time: {process_time:.2f} seconds")
    return response

def run_app(**kwargs: Any) -> None:
    """Run application"""
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, **kwargs)

if __name__ == "__main__":
    run_app(host="0.0.0.0", port=8000, reload=True) 