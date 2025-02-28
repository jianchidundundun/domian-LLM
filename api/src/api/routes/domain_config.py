from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
from src.core.db.domain_db import DomainDB
from src.core.db.config import get_db
import logging
import aiofiles
import os
from pathlib import Path
from src.models.domain_models import Document
from sqlalchemy import select
from fastapi.responses import JSONResponse

router = APIRouter()

logger = logging.getLogger(__name__)

class DomainCreate(BaseModel):
    name: str
    description: str

class OperationCreate(BaseModel):
    domain_name: str
    operation_id: str
    description: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]

class TemplateCreate(BaseModel):
    domain_name: str
    name: str
    template: str
    required_variables: List[str]

@router.post("/domains")
async def create_domain(domain: DomainCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await DomainDB.create_domain(domain.name, domain.description, db)
        return JSONResponse(
            content={"status": "success", "domain_id": result.id},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Failed to create domain: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@router.get("/domains")
async def list_domains(db: AsyncSession = Depends(get_db)):
    try:
        logger.info("Getting all domains...")
        domains = await DomainDB.get_all_domains(db)
        logger.info(f"Found {len(domains)} domains")
        # Convert to JSON format
        result = [
            {
                "id": domain.id,
                "name": domain.name,
                "description": domain.description
            }
            for domain in domains
        ]
        logger.info(f"Domain data: {result}")
        return JSONResponse(
            content={"domains": result},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Failed to get domain list: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@router.post("/operations")
async def add_operation(
    operation: OperationCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await DomainDB.add_operation(
            operation.domain_name,
            operation.operation_id,
            operation.description,
            operation.parameters,
            operation.examples,
            db
        )
        return {"status": "success", "operation_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    domain_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Ensure upload directory exists
        upload_dir = Path("data/documents")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Read file content
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Save to database
        document = Document(
            domain_id=domain_id,
            filename=file.filename,
            content=content
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.filename
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(
    domain_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Document)
            .where(Document.domain_id == domain_id)
            .order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "created_at": doc.created_at
                }
                for doc in documents
            ]
        }
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 