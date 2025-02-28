import pytest
import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """运行所有测试"""
    pytest.main(["-v", "tests/"])

if __name__ == "__main__":
    run_tests() 