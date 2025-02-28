import pytest
from fastapi.testclient import TestClient
import numpy as np
from src.matlab.server import matlab_app
import json
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("src.matlab.server")

# 使用新版本的 TestClient 初始化方式
client = TestClient(matlab_app, base_url="http://test")

def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_basic_math():
    """测试基础数学运算"""
    # 测试加法
    response = client.post("/execute", json={
        "function": "plus",
        "args": [1, 2]
    })
    assert response.status_code == 200
    assert response.json()["result"] == 3.0
    
    # 测试除法
    response = client.post("/execute", json={
        "function": "divide",
        "args": [6, 2]
    })
    assert response.status_code == 200
    assert response.json()["result"] == 3.0
    
    # 测试除零错误
    response = client.post("/execute", json={
        "function": "divide",
        "args": [1, 0]
    })
    assert response.json()["success"] == False
    assert "除数不能为0" in response.json()["error"]

def test_signal_processing():
    """测试信号处理功能"""
    # 生成测试信号
    t = np.linspace(0, 1, 100)
    signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)
    
    # 测试FFT
    response = client.post("/execute", json={
        "function": "fft",
        "args": [signal.tolist()]
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert "frequencies" in result
    assert "magnitude" in result
    assert "phase" in result
    
    # 测试低通滤波
    response = client.post("/execute", json={
        "function": "lowpass",
        "args": [signal.tolist(), 15.0, 100.0]
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert "filtered_signal" in result
    assert "filter_coefficients" in result

def test_filter_functions():
    """测试滤波器功能"""
    # 生成测试信号
    t = np.linspace(0, 1, 1000)
    signal = (np.sin(2 * np.pi * 5 * t) + 
             np.sin(2 * np.pi * 50 * t) + 
             np.random.normal(0, 0.1, len(t)))
    
    # 测试低通滤波器
    response = client.post("/execute", json={
        "function": "lowpass",
        "args": [signal.tolist(), 10.0, 1000.0]
    })
    assert response.status_code == 200
    result = response.json()["result"]
    filtered_signal = np.array(result["filtered_signal"])
    assert len(filtered_signal) == len(signal)
    
    # 测试高通滤波器
    response = client.post("/execute", json={
        "function": "highpass",
        "args": [signal.tolist(), 30.0, 1000.0]
    })
    assert response.status_code == 200
    result = response.json()["result"]
    filtered_signal = np.array(result["filtered_signal"])
    assert len(filtered_signal) == len(signal)
    
    # 测试带通滤波器
    response = client.post("/execute", json={
        "function": "bandpass",
        "args": [signal.tolist(), 20.0, 40.0, 1000.0]
    })
    assert response.status_code == 200
    result = response.json()["result"]
    filtered_signal = np.array(result["filtered_signal"])
    assert len(filtered_signal) == len(signal)

def test_error_handling():
    """测试错误处理"""
    # 测试未知函数
    response = client.post("/execute", json={
        "function": "unknown_function",
        "args": []
    })
    assert response.json()["success"] == False
    assert "未知的函数" in response.json()["error"]
    
    # 测试参数错误
    response = client.post("/execute", json={
        "function": "lowpass",
        "args": [[], 0, 0]  # 空信号和无效参数
    })
    assert response.json()["success"] == False

def test_filter_unknown_function():
    """测试 filter 未知函数错误
    对应错误日志：
    2025-02-28 17:40:43,513 - src.matlab.server - ERROR - 函数执行失败 filter: 未知的函数: filter
    """
    response = client.post("/execute", json={
        "session_id": "test_session",
        "function": "filter",
        "args": [[1.0, 2.0, 3.0, 4.0, 5.0]],
        "kwargs": {}
    })
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == False
    assert "未知的函数: filter" in result["error"]

def test_fft_tuple_index_error():
    """测试 FFT 空数组导致的索引错误
    对应错误日志：
    2025-02-28 17:41:00,033 - src.matlab.server - ERROR - FFT计算失败: Invalid number of FFT data points (0) specified.
    """
    response = client.post("/execute", json={
        "session_id": "test_session",
        "function": "fft",
        "args": [[]],  # 传入空数组触发索引错误
        "kwargs": {}
    })
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == False
    assert "Invalid number of FFT data points (0) specified" in result["error"]

def test_filter_with_invalid_params():
    """测试带参数的 filter 未知函数错误
    对应错误日志：
    2025-02-28 17:41:29,718 - src.matlab.server - ERROR - 函数执行失败 filter: 未知的函数: filter
    """
    response = client.post("/execute", json={
        "session_id": "test_session",
        "function": "filter",
        "args": [[1.0, 2.0, 3.0, 4.0, 5.0]],
        "kwargs": {
            "b": [1.0],
            "a": [1.0]
        }
    })
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == False
    assert "未知的函数: filter" in result["error"]

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 