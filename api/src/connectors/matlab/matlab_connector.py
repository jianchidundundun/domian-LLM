from typing import Dict, Any, Optional
import aiohttp
from ..base_connector import BaseConnector

class MatlabConnector(BaseConnector):
    def __init__(
        self,
        name: str = "matlab",
        server_url: str = "http://localhost:8001"  # 使用独立服务器的端口
    ):
        super().__init__(name)
        self.server_url = server_url
        self.session_id = "default"
        
    async def execute(self, task: Dict[str, Any]) -> Any:
        """执行MATLAB任务"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/execute",
                json={
                    "session_id": self.session_id,
                    "function": task["function"],
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {})
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"MATLAB执行错误: {await response.text()}")
                result = await response.json()
                return result["result"] 