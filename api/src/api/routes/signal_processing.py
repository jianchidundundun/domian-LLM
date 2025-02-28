from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from src.adapter.adapter_manager import AdapterManager
from pydantic import BaseModel
import numpy as np

router = APIRouter()
adapter_manager = AdapterManager()

class FilterRequest(BaseModel):
    data: List[float]
    filter_type: str
    parameters: Dict[str, Any] = None

class SignalProcessingRequest(BaseModel):
    signal: List[float]
    sampling_rate: float
    process_type: str
    parameters: Dict[str, Any] = {}

class SignalProcessingResponse(BaseModel):
    original_signal: List[float]
    processed_signal: List[float]
    spectrum: List[float] = None
    sampling_rate: float
    process_type: str

@router.post("/filter")
async def apply_filter(request: FilterRequest):
    try:
        # 根据filter_type选择合适的滤波器参数
        filter_params = get_filter_params(request.filter_type)
        
        # 调用MATLAB滤波器
        result = await adapter_manager.execute_task(
            "matlab",
            {
                "function": "filter",
                "args": [request.data],
                "kwargs": {
                    "b": filter_params["b"],
                    "a": filter_params["a"]
                }
            }
        )
        
        return {
            "filtered_data": result,
            "filter_type": request.filter_type,
            "parameters": filter_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=SignalProcessingResponse)
async def process_signal(request: SignalProcessingRequest):
    try:
        # 执行信号处理
        result = await adapter_manager.execute_task(
            "matlab",
            {
                "function": request.process_type,
                "args": [request.signal],
                "kwargs": {
                    "sampling_rate": request.sampling_rate,
                    **request.parameters
                }
            }
        )

        # 计算频谱
        spectrum = await adapter_manager.execute_task(
            "matlab",
            {
                "function": "fft",
                "args": [request.signal]
            }
        )

        return SignalProcessingResponse(
            original_signal=request.signal,
            processed_signal=result,
            spectrum=spectrum,
            sampling_rate=request.sampling_rate,
            process_type=request.process_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_filter_params(filter_type: str) -> Dict[str, List[float]]:
    """获取预定义的滤波器参数"""
    params = {
        "moving_average": {
            "b": [0.2, 0.2, 0.2, 0.2, 0.2],
            "a": [1.0]
        },
        "low_pass": {
            "b": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            "a": [1.0]
        },
        "custom": {
            "b": [1.0, -0.5],
            "a": [1.0]
        }
    }
    
    return params.get(filter_type, params["moving_average"]) 