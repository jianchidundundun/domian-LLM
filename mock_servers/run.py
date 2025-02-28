import uvicorn
from src.matlab.server import matlab_app

def main():
    # 启动MATLAB模拟服务器
    uvicorn.run(matlab_app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main() 