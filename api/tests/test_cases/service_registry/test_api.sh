#!/bin/bash

# 设置 API 基础 URL
API_BASE="http://127.0.0.1:8000/api/v1"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始服务注册测试...${NC}\n"

# 1. 创建信号处理领域
echo "1. 创建信号处理领域..."
curl -X POST "$API_BASE/domains" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "信号处理",
    "description": "这是一个信号处理领域"
  }' | json_pp

sleep 1

# 2. 注册 MATLAB 滤波器服务
echo -e "\n2. 注册 MATLAB 滤波器服务..."
curl -X POST "$API_BASE/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "matlab_filters",
    "description": "MATLAB 滤波器服务",
    "endpoint_url": "http://localhost:8001/matlab",
    "service_type": "matlab",
    "methods": {
      "lowpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float",
          "sampling_rate": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      },
      "highpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float",
          "sampling_rate": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      },
      "bandpass": {
        "parameters": {
          "signal": "array",
          "low_cutoff": "float",
          "high_cutoff": "float",
          "sampling_rate": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      }
    }
  }' | json_pp

sleep 1

# 3. 查询已注册的服务
echo -e "\n3. 查询已注册的服务..."
curl "$API_BASE/services/信号处理" | json_pp

sleep 1

# 4. 测试注册重复服务（应该更新而不是报错）
echo -e "\n4. 测试更新现有服务..."
curl -X POST "$API_BASE/services/register" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "matlab_filters",
    "description": "更新后的 MATLAB 滤波器服务",
    "endpoint_url": "http://localhost:8001/matlab",
    "service_type": "matlab",
    "methods": {
      "lowpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float",
          "sampling_rate": "float"
        },
        "returns": {
          "filtered_signal": "array"
        }
      }
    }
  }' | json_pp

sleep 1

# 5. 再次查询服务（检查更新结果）
echo -e "\n5. 查询更新后的服务..."
curl "$API_BASE/services/信号处理" | json_pp

sleep 1

# 6. 测试停用服务
echo -e "\n6. 测试停用服务..."
curl -X DELETE "$API_BASE/services/1" | json_pp

sleep 1

# 7. 最后查询（应该看不到被停用的服务）
echo -e "\n7. 查询服务列表（应该为空）..."
curl "$API_BASE/services/信号处理" | json_pp

echo -e "\n${GREEN}服务注册测试完成${NC}" 