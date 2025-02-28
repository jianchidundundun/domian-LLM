#!/bin/bash

# 设置API基础URL
API_BASE="http://127.0.0.1:8000/api/v1"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 设置curl默认选项
CURL_OPTS="-H 'Content-Type: application/json; charset=utf-8' -H 'Accept: application/json; charset=utf-8'"

echo -e "${GREEN}开始测试LLM执行功能...${NC}\n"

# 1. 创建信号处理领域
echo "1. 创建信号处理领域..."
curl -X POST "$API_BASE/domains" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Accept: application/json; charset=utf-8" \
  -d '{
    "name": "信号处理",
    "description": "用于处理各种信号的领域"
  }' | python3 -m json.tool

sleep 2

# 2. 注册MATLAB滤波器服务
echo -e "\n2. 注册MATLAB滤波器服务..."
curl -X POST "$API_BASE/services/register" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Accept: application/json; charset=utf-8" \
  -d '{
    "domain_name": "信号处理",
    "service_name": "matlab_filter",
    "description": "MATLAB滤波器服务",
    "endpoint_url": "http://localhost:8001",
    "service_type": "matlab",
    "methods": {
      "lowpass": {
        "parameters": {
          "signal": "array",
          "cutoff_freq": "float",
          "sampling_rate": "float"
        },
        "returns": "array"
      }
    }
  }' | python3 -m json.tool

sleep 2

# 3. 创建测试文档
echo -e "\n3. 创建测试文档..."
cat > test_doc.txt << EOF
数字滤波器基础知识：
1. 低通滤波器：用于去除高频噪声，保留低频信号
2. 高通滤波器：用于去除低频干扰，保留高频信号
3. 带通滤波器：只允许特定频率范围内的信号通过
EOF

echo "上传文档到API..."
curl -X POST "$API_BASE/documents/upload" \
  -H "Accept: application/json; charset=utf-8" \
  -F "file=@test_doc.txt" \
  -F "domain_id=1" | python3 -m json.tool

sleep 2

# 4. 测试LLM执行
echo -e "\n4. 测试LLM执行 - 低通滤波..."
curl -X POST "$API_BASE/llm/execute" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Accept: application/json; charset=utf-8" \
  -d '{
    "query": "如何使用低通滤波器处理信号？",
    "domain_name": "信号处理"
  }' | python3 -m json.tool

# 清理测试文件
rm test_doc.txt

echo -e "\n${GREEN}测试完成${NC}" 