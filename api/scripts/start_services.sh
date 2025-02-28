#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 设置端口
API_PORT=8000

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在停止API服务...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        wait $API_PID 2>/dev/null
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

# 等待服务启动
wait_for_service() {
    local port=$1
    local name=$2
    local pid=$3
    local max_retries=30
    local retry_count=0
    
    echo "等待 $name 启动..."
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:$port/health > /dev/null; then
            echo -e "${GREEN}$name 启动成功 (PID: $pid)${NC}"
            return 0
        fi
        retry_count=$((retry_count + 1))
        if [ $retry_count -eq $max_retries ]; then
            echo -e "${RED}错误: $name 启动失败${NC}"
            return 1
        fi
        echo -n "."
        sleep 1
    done
}

echo -e "${GREEN}启动API服务...${NC}\n"

# 检查poetry是否安装
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}错误: 未找到poetry，请先安装poetry${NC}"
    echo "可以使用以下命令安装："
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# 检查API端口
if ! check_port $API_PORT; then
    cleanup
    exit 1
fi

# 提示用户启动MATLAB服务器
echo -e "\n${BLUE}请确保已经手动启动MATLAB服务器：${NC}"
echo -e "1. 打开新的终端窗口"
echo -e "2. 进入mock_servers目录：${YELLOW}cd $PROJECT_ROOT/mock_servers${NC}"
echo -e "3. 安装依赖：${YELLOW}poetry install${NC}"
echo -e "4. 启动服务器：${YELLOW}poetry run python run.py${NC}"
echo -e "${BLUE}按回车键继续...${NC}"
read

# 启动主API服务器
echo -e "\n${GREEN}启动主API服务器...${NC}"
cd "$PROJECT_ROOT"
if ! poetry install; then
    echo -e "${RED}错误: API服务器依赖安装失败${NC}"
    cleanup
    exit 1
fi
poetry run python run.py &
API_PID=$!

# 等待API服务器启动
if ! wait_for_service $API_PORT "API服务器" $API_PID; then
    cleanup
    exit 1
fi

echo -e "\n${GREEN}API服务器启动完成！${NC}"
echo -e "API服务器运行在: http://localhost:$API_PORT"

# 询问是否运行demo
echo -e "\n${BLUE}是否要运行demo测试？(y/n)${NC}"
read run_demo

if [ "$run_demo" = "y" ] || [ "$run_demo" = "Y" ]; then
    echo -e "\n${GREEN}运行demo测试...${NC}"
    cd "$PROJECT_ROOT"
    poetry run python scripts/demo.py
fi

echo -e "\n${YELLOW}提示: 按 Ctrl+C 停止API服务${NC}"

# 等待API服务器进程结束
wait $API_PID
cleanup 