#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 设置服务器端口
MATLAB_PORT=8001

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在停止服务器...${NC}"
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 检查端口是否被占用
check_port() {
    if lsof -i :$1 > /dev/null; then
        echo -e "${RED}错误: 端口 $1 已被占用${NC}"
        return 1
    fi
    return 0
}

echo -e "${GREEN}启动模拟服务器...${NC}"

# 检查poetry是否安装
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}错误: 未找到poetry，请先安装poetry${NC}"
    echo "可以使用以下命令安装："
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# 检查依赖
echo -e "${GREEN}检查依赖...${NC}"
poetry install

# 检查端口
if ! check_port $MATLAB_PORT; then
    exit 1
fi

# 启动服务器
echo -e "${GREEN}启动MATLAB模拟服务器...${NC}"
poetry run python run.py &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:$MATLAB_PORT/health > /dev/null; then
        echo -e "${GREEN}MATLAB服务器启动成功 (PID: $SERVER_PID)${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    if [ $retry_count -eq $max_retries ]; then
        echo -e "${RED}错误: MATLAB服务器启动失败${NC}"
        cleanup
        exit 1
    fi
    echo -n "."
    sleep 1
done

echo -e "\n${GREEN}所有服务启动完成！${NC}"
echo -e "MATLAB服务器运行在: http://localhost:$MATLAB_PORT"
echo -e "\n${YELLOW}提示: 按 Ctrl+C 停止所有服务${NC}"

# 等待用户中断
wait $SERVER_PID 