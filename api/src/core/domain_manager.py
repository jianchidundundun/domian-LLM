from typing import Dict, Optional, Type, Any
from .domains.base_domain import BaseDomain, DomainOperation
from .db.domain_db import DomainDB
from .domains.signal_processing import SignalProcessingDomain

class DomainManager:
    def __init__(self):
        self.db = DomainDB()
        self.domains: Dict[str, BaseDomain] = {}
        self._load_domains()
        
    def _load_domains(self) -> None:
        """从数据库加载所有领域"""
        with self.db.Session() as session:
            domains = session.query(Domain).all()
            for domain in domains:
                self._load_domain(domain)
                
    def _load_domain(self, domain_data: Domain) -> None:
        """加载单个领域的配置"""
        domain = BaseDomain(domain_data.name)
        
        # 加载操作
        for op in domain_data.operations:
            domain.register_operation(DomainOperation(
                operation_id=op.operation_id,
                description=op.description,
                parameters=op.parameters,
                examples=op.examples
            ))
            
        self.domains[domain_data.name] = domain
        
    def _register_default_domains(self) -> None:
        """注册默认的领域"""
        self.register_domain(SignalProcessingDomain())
        # 可以注册更多领域...
        
    def register_domain(self, domain: BaseDomain) -> None:
        """注册新的领域"""
        self.domains[domain.name] = domain
        
    def get_domain(self, name: str) -> Optional[BaseDomain]:
        """获取领域实例"""
        return self.domains.get(name)
        
    async def execute_operation(
        self,
        domain_name: str,
        operation_id: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """执行领域操作"""
        domain = self.get_domain(domain_name)
        if not domain:
            raise ValueError(f"未知的领域: {domain_name}")
            
        operation = domain.get_operation(operation_id)
        if not operation:
            raise ValueError(f"未知的操作: {operation_id}")
            
        # 这里可以添加参数验证等逻辑
        return await self._execute_operation(domain, operation, parameters) 