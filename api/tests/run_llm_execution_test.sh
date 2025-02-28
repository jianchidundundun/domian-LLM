#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 创建日志目录
LOG_DIR="tests/logs"
mkdir -p $LOG_DIR

# 设置日志文件
LOG_FILE="$LOG_DIR/test_$(date +%Y%m%d_%H%M%S).log"

echo -e "${GREEN}开始运行执行器测试...${NC}\n"
echo "日志将保存到: $LOG_FILE"

# 运行测试并保存日志
poetry run pytest tests/test_llm_execution_flow.py -v --log-cli-level=DEBUG 2>&1 | tee $LOG_FILE

# 检查测试结果
TEST_RESULT=${PIPESTATUS[0]}
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}测试成功完成${NC}"
else
    echo -e "\n${RED}测试失败${NC}"
    echo -e "请查看日志文件了解详细信息: $LOG_FILE"
fi

exit $TEST_RESULT 