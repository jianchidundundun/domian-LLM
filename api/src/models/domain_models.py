from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Domain(Base):
    """领域模型"""
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    
    # 关联
    concepts = relationship("Concept", back_populates="domain")
    operations = relationship("Operation", back_populates="domain")
    documents = relationship("Document", back_populates="domain")
    templates = relationship("PromptTemplate", back_populates="domain")
    services = relationship("ServiceEndpoint", back_populates="domain")

class Concept(Base):
    """领域概念"""
    __tablename__ = "concepts"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    name = Column(String)
    description = Column(String)
    
    domain = relationship("Domain", back_populates="concepts")

class Operation(Base):
    """领域操作"""
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    operation_id = Column(String, unique=True)
    description = Column(String)
    parameters = Column(JSON)  # 存储参数定义
    examples = Column(JSON)    # 存储示例
    
    domain = relationship("Domain", back_populates="operations")

class Document(Base):
    """领域文档"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    filename = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    domain = relationship("Domain", back_populates="documents")

class PromptTemplate(Base):
    """提示词模板"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    name = Column(String)
    template = Column(String)
    required_variables = Column(JSON)
    
    domain = relationship("Domain", back_populates="templates")

class ServiceEndpoint(Base):
    """领域服务端点"""
    __tablename__ = "service_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    name = Column(String)  # 服务名称
    description = Column(String)  # 服务描述
    endpoint_url = Column(String)  # 服务URL
    service_type = Column(String)  # 服务类型（如 'matlab', 'python' 等）
    methods = Column(JSON)  # 支持的方法和参数
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    domain = relationship("Domain", back_populates="services") 