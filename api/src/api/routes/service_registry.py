from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel, HttpUrl
from src.core.db.config import get_db
from src.models.domain_models import ServiceEndpoint, Domain
from sqlalchemy import select
import logging
from src.core.config.service_config import ServiceConfig

router = APIRouter()
logger = logging.getLogger(__name__)
service_config = ServiceConfig()

class ServiceRegistration(BaseModel):
    domain_name: str
    service_name: str
    description: str
    endpoint_url: HttpUrl
    service_type: str
    methods: Dict[str, Dict[str, Any]] = None  # Optional, if not provided, load from configuration

@router.post("/services/register")
async def register_service(
    service: ServiceRegistration,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Find domain
        stmt = select(Domain).where(Domain.name == service.domain_name)
        result = await db.execute(stmt)
        domain = result.scalar_one_or_none()
        
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain not found: {service.domain_name}")
            
        # Load service method definitions from configuration
        if service.methods is None:
            config = service_config.get_service_config(service.service_type, service.domain_name)
            if not config:
                raise HTTPException(
                    status_code=400,
                    detail=f"Service configuration not found: {service.service_type}.{service.domain_name}"
                )
            methods = config.get("methods", {})
        else:
            methods = service.methods
            
        # Create service endpoint
        service_endpoint = ServiceEndpoint(
            domain_id=domain.id,
            name=service.service_name,
            description=service.description,
            endpoint_url=str(service.endpoint_url),
            service_type=service.service_type,
            methods=methods
        )
        
        # Check if service already exists
        result = await db.execute(
            select(ServiceEndpoint).where(
                ServiceEndpoint.domain_id == domain.id,
                ServiceEndpoint.name == service.service_name
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing service
            existing.description = service.description
            existing.endpoint_url = str(service.endpoint_url)
            existing.methods = methods
            existing.is_active = True
        else:
            # Create new service
            db.add(service_endpoint)
        
        await db.commit()
        return {"status": "success", "message": "Service registered successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{domain_name}")
async def list_services(domain_name: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Getting services for domain '{domain_name}'...")
        # Get domain
        domain = await db.execute(
            select(Domain).where(Domain.name == domain_name)
        )
        domain = domain.scalar_one_or_none()
        
        if not domain:
            logger.warning(f"未找到领域: {domain_name}")
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
            
        # 获取服务
        services = await db.execute(
            select(ServiceEndpoint)
            .where(ServiceEndpoint.domain_id == domain.id)
            .where(ServiceEndpoint.is_active == True)
        )
        services = services.scalars().all()
        
        logger.info(f"找到 {len(services)} 个服务")
        
        result = {
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "endpoint_url": service.endpoint_url,
                    "service_type": service.service_type,
                    "methods": service.methods
                }
                for service in services
            ]
        }
        logger.info(f"服务数据: {result}")
        return result
    except Exception as e:
        logger.error(f"获取服务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/services/{service_id}")
async def deactivate_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(ServiceEndpoint).where(ServiceEndpoint.id == service_id)
        )
        service = result.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
            
        service.is_active = False
        await db.commit()
        return {"status": "success", "message": "Service deactivated"}
    except Exception as e:
        logger.error(f"Error deactivating service: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 