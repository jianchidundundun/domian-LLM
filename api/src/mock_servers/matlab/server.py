from fastapi import FastAPI, HTTPException
import numpy as np
from typing import Dict, Any, List
import json

matlab_app = FastAPI(title="Mock MATLAB Server")

class MatlabSession:
    def __init__(self):
        self.workspace: Dict[str, Any] = {}
        
    def set_variable(self, name: str, value: Any) -> None:
        self.workspace[name] = value
        
    def get_variable(self, name: str) -> Any:
        return self.workspace.get(name)

# 全局会话管理
sessions: Dict[str, MatlabSession] = {}

@matlab_app.post("/execute")
async def execute_command(command: Dict[str, Any]):
    try:
        session_id = command.get("session_id", "default")
        if session_id not in sessions:
            sessions[session_id] = MatlabSession()
            
        func_name = command["function"]
        args = command.get("args", [])
        kwargs = command.get("kwargs", {})
        
        # 执行模拟的MATLAB函数
        result = await execute_matlab_function(
            sessions[session_id],
            func_name,
            args,
            kwargs
        )
        
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_matlab_function(
    session: MatlabSession,
    func_name: str,
    args: List[Any],
    kwargs: Dict[str, Any]
) -> Any:
    # 基础数学运算
    if func_name == "plus":
        return float(args[0]) + float(args[1])
    elif func_name == "minus":
        return float(args[0]) - float(args[1])
    elif func_name == "times":
        return float(args[0]) * float(args[1])
    # 信号处理
    elif func_name == "fft":
        data = np.array(args[0])
        return np.fft.fft(data).tolist()
    elif func_name == "filter":
        b = np.array(kwargs.get("b", [1.0]))
        a = np.array(kwargs.get("a", [1.0]))
        x = np.array(args[0])
        return list(np.convolve(b, x) / a[0])
    else:
        raise ValueError(f"未知的MATLAB函数: {func_name}") 