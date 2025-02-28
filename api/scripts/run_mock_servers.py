import uvicorn
from src.mock_servers.matlab.server import matlab_app

def run_matlab_server():
    uvicorn.run(matlab_app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    run_matlab_server() 