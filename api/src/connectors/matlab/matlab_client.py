from typing import Dict, Any, List
import aiohttp

class MatlabClient:
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.session_id = "default"
    
    async def execute_function(
        self,
        function_name: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> Any:
        """执行MATLAB函数"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/execute",
                json={
                    "session_id": self.session_id,
                    "function": function_name,
                    "args": args or [],
                    "kwargs": kwargs or {}
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"MATLAB执行错误: {await response.text()}")
                return (await response.json())["result"] 