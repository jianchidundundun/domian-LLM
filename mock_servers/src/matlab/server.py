from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import signal
import logging
import json
from .functions.basic_math import BasicMath
from .functions.signal_processing import SignalProcessing, FilterFunctions

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

matlab_app = FastAPI(
    title="MATLAB Mock Server",
    description="模拟MATLAB服务器API",
    version="0.1.0"
)

class MatlabSession:
    def __init__(self):
        self.variables = {}
        self.basic_math = BasicMath()
        self.signal_processor = SignalProcessing()
        self.filter_functions = FilterFunctions()
        
    def execute_function(self, func_name: str, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        """执行MATLAB函数"""
        try:
            # 基础数学运算
            if hasattr(self.basic_math, func_name):
                return getattr(self.basic_math, func_name)(*args, **kwargs)
                
            # 信号处理
            if hasattr(self.signal_processor, func_name):
                return getattr(self.signal_processor, func_name)(*args, **kwargs)
                
            # 滤波器
            if hasattr(self.filter_functions, func_name):
                return getattr(self.filter_functions, func_name)(*args, **kwargs)
                
            raise ValueError(f"未知的函数: {func_name}")
            
        except Exception as e:
            logger.error(f"函数执行失败 {func_name}: {str(e)}")
            raise

class BasicMath:
    def plus(self, a: float, b: float) -> float:
        """加法"""
        return float(a) + float(b)
        
    def minus(self, a: float, b: float) -> float:
        """减法"""
        return float(a) - float(b)
        
    def times(self, a: float, b: float) -> float:
        """乘法"""
        return float(a) * float(b)
        
    def divide(self, a: float, b: float) -> float:
        """除法"""
        if float(b) == 0:
            raise ValueError("除数不能为0")
        return float(a) / float(b)

class SignalProcessing:
    def fft(self, data: List[float]) -> Dict[str, List[float]]:
        """傅里叶变换"""
        try:
            # 转换为numpy数组
            signal = np.array(data)
            # 计算FFT
            fft_result = np.fft.fft(signal)
            # 计算频率
            freqs = np.fft.fftfreq(len(signal))
            # 计算幅度谱
            magnitude = np.abs(fft_result)
            
            return {
                "frequencies": freqs.tolist(),
                "magnitude": magnitude.tolist(),
                "phase": np.angle(fft_result).tolist()
            }
        except Exception as e:
            logger.error(f"FFT计算失败: {str(e)}")
            raise
            
    def ifft(self, data: List[complex]) -> List[float]:
        """逆傅里叶变换"""
        try:
            signal = np.array(data)
            result = np.fft.ifft(signal)
            return result.real.tolist()
        except Exception as e:
            logger.error(f"IFFT计算失败: {str(e)}")
            raise

class FilterFunctions:
    def lowpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """低通滤波器"""
        try:
            # 设计滤波器
            nyquist = sampling_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            b, a = signal.butter(4, normalized_cutoff, btype='low')
            
            # 应用滤波器
            filtered = signal.filtfilt(b, a, signal_data)
            
            return {
                "filtered_signal": filtered.tolist(),
                "filter_coefficients": {
                    "b": b.tolist(),
                    "a": a.tolist()
                }
            }
        except Exception as e:
            logger.error(f"低通滤波失败: {str(e)}")
            raise
            
    def highpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """高通滤波器"""
        try:
            nyquist = sampling_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            filtered = signal.filtfilt(b, a, signal_data)
            
            return {
                "filtered_signal": filtered.tolist(),
                "filter_coefficients": {
                    "b": b.tolist(),
                    "a": a.tolist()
                }
            }
        except Exception as e:
            logger.error(f"高通滤波失败: {str(e)}")
            raise
            
    def bandpass(
        self, 
        signal_data: List[float], 
        low_cutoff: float, 
        high_cutoff: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """带通滤波器"""
        try:
            nyquist = sampling_rate / 2
            normalized_cutoffs = [low_cutoff / nyquist, high_cutoff / nyquist]
            b, a = signal.butter(4, normalized_cutoffs, btype='band')
            filtered = signal.filtfilt(b, a, signal_data)
            
            return {
                "filtered_signal": filtered.tolist(),
                "filter_coefficients": {
                    "b": b.tolist(),
                    "a": a.tolist()
                }
            }
        except Exception as e:
            logger.error(f"带通滤波失败: {str(e)}")
            raise

# 全局会话存储
sessions: Dict[str, MatlabSession] = {}

def get_or_create_session(session_id: str = "default") -> MatlabSession:
    """获取或创建会话"""
    if session_id not in sessions:
        sessions[session_id] = MatlabSession()
    return sessions[session_id]

@matlab_app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}

@matlab_app.post("/execute")
async def execute_command(command: Dict[str, Any]):
    """执行MATLAB命令"""
    try:
        # 获取会话
        session_id = command.get("session_id", "default")
        session = get_or_create_session(session_id)
        
        # 执行函数
        function_name = command.get("function")
        if not function_name:
            raise HTTPException(status_code=400, detail="缺少function参数")
            
        args = command.get("args", [])
        kwargs = command.get("kwargs", {})
        
        # 执行函数并返回结果
        result = session.execute_function(function_name, args, kwargs)
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"命令执行失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 