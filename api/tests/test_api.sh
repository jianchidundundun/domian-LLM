#!/bin/bash

# 设置 API 基础 URL
API_BASE="http://127.0.0.1:8000/api/v1"

# 测试创建领域
echo "测试创建领域..."
curl -X POST "$API_BASE/domains" \
  -H "Content-Type: application/json" \
  -d '{"name":"信号处理","description":"这是一个信号处理领域"}' | json_pp

# 等待 1 秒
sleep 1

# 测试获取领域列表
echo -e "\n获取领域列表..."
curl "$API_BASE/domains" | json_pp

# 等待 1 秒
sleep 1

# 创建测试文档
echo "信号处理基础概念..." > test_documents.txt

# 测试上传文档
echo -e "\n上传文档..."
curl -X POST "$API_BASE/documents/upload" \
  -F "file=@test_documents.txt" \
  -F "domain_id=1" | json_pp

# 等待 1 秒
sleep 1

# 测试获取文档列表
echo -e "\n获取文档列表..."
curl "$API_BASE/documents?domain_id=1" | json_pp

# 清理测试文件
rm test_documents.txt 