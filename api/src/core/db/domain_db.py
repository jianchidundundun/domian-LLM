from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert
from typing import List, Dict, Any, Optional
from ...models.domain_models import Base, Domain, Concept, Operation, Document, PromptTemplate
from .config import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainDB:
    @staticmethod
    async def init_db():
        """初始化数据库"""
        async with engine.begin() as conn:
            # 删除所有表
            await conn.run_sync(Base.metadata.drop_all)
            # 重新创建所有表
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def create_domain(name: str, description: str, session: AsyncSession) -> Domain:
        """创建新领域"""
        try:
            logger.info(f"Creating domain with name: {name}, description: {description}")
            domain = Domain(name=name, description=description)
            session.add(domain)
            await session.commit()
            await session.refresh(domain)
            logger.info(f"Domain created successfully: {domain.id}")
            return domain
        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            await session.rollback()
            raise e
    
    @staticmethod
    async def add_operation(
        domain_name: str,
        operation_id: str,
        description: str,
        parameters: Dict[str, Any],
        examples: List[Dict[str, Any]],
        session: AsyncSession
    ) -> Operation:
        """添加领域操作"""
        try:
            result = await session.execute(
                select(Domain).where(Domain.name == domain_name)
            )
            domain = result.scalar_one_or_none()
            if not domain:
                raise ValueError(f"Domain {domain_name} not found")

            operation = Operation(
                domain_id=domain.id,
                operation_id=operation_id,
                description=description,
                parameters=parameters,
                examples=examples
            )
            session.add(operation)
            await session.commit()
            await session.refresh(operation)
            return operation
        except Exception as e:
            await session.rollback()
            raise e
    
    @staticmethod
    async def add_template(
        domain_name: str,
        name: str,
        template: str,
        required_variables: List[str],
        session: AsyncSession
    ) -> PromptTemplate:
        """添加提示词模板"""
        result = await session.execute(
            select(Domain).where(Domain.name == domain_name)
        )
        domain = result.scalar_one_or_none()
        
        if not domain:
            raise ValueError(f"Domain not found: {domain_name}")
        
        template_obj = PromptTemplate(
            domain_id=domain.id,
            name=name,
            template=template,
            required_variables=required_variables
        )
        session.add(template_obj)
        await session.commit()
        await session.refresh(template_obj)
        return template_obj
    
    @staticmethod
    async def get_all_domains(session: AsyncSession) -> List[Domain]:
        """获取所有领域"""
        try:
            result = await session.execute(select(Domain))
            return result.scalars().all()
        except Exception as e:
            await session.rollback()
            raise e
    
    @staticmethod
    async def get_domain_operations(
        domain_name: str,
        session: AsyncSession
    ) -> List[Operation]:
        """获取领域的所有操作"""
        result = await session.execute(
            select(Operation)
            .join(Domain)
            .where(Domain.name == domain_name)
        )
        return result.scalars().all() 