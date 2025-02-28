from typing import Dict, Any, Optional
from src.connectors.base_connector import BaseConnector
from src.connectors.matlab.matlab_connector import MatlabConnector

class AdapterManager:
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self._register_default_connectors()
        
    def _register_default_connectors(self) -> None:
        """注册默认连接器"""
        self.register_connector("matlab", MatlabConnector())
        
    def register_connector(self, name: str, connector: BaseConnector) -> None:
        self.connectors[name] = connector
        
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        return self.connectors.get(name)
        
    async def execute_task(self, connector_name: str, task: Dict[str, Any]) -> Optional[Any]:
        connector = self.get_connector(connector_name)
        if connector:
            return await connector.execute(task)
        return None 