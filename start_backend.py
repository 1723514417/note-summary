import os
import sys
import subprocess

# 设置工作目录为backend目录
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# 设置PYTHONPATH环境变量
sys.path.insert(0, os.path.abspath('.'))

# 启动后端服务
print("启动后端服务...")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.executable}")

# 构建命令
command = [
    os.path.join('venv', 'Scripts', 'python.exe'),
    '-m', 'uvicorn',
    'app.main:app',
    '--host', '127.0.0.1',
    '--port', '8000'
]

print(f"执行命令: {' '.join(command)}")

# 执行命令
subprocess.run(command)
