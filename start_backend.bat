@echo off

REM 设置PYTHONPATH环境变量
set PYTHONPATH=D:\aicode\note-summary\backend

REM 运行后端服务
echo 启动后端服务...
D:\aicode\note-summary\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
