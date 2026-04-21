@echo off

REM 启动后端服务
echo 启动后端服务...
cd backend
start "Backend Server" venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

REM 等待2秒让后端服务启动
echo 等待后端服务启动...
timeout /t 2 /nobreak >nul

REM 启动前端服务
echo 启动前端服务...
cd ..
cd frontend
start "Frontend Server" npm run dev

REM 打开浏览器访问前端
echo 服务启动完成，打开浏览器访问 http://localhost:3000
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo 服务启动完成！
