#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始运行执行器测试...${NC}\n"

# 运行测试
poetry run pytest tests/test_execution.py -v

# 检查测试结果
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}测试成功完成${NC}"
else
    echo -e "\n${RED}测试失败${NC}"
fi 