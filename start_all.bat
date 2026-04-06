@echo off
chcp 65001 >nul
title 养老机构健康监测系统
echo ========================================
echo   养老机构健康监测与风险预警系统
echo   启动脚本
echo ========================================
echo.
echo 正在启动后端服务...
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo 正在启动前端服务...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo 服务启动中...
echo.
echo 后端API: http://localhost:8000
echo 前端界面: http://localhost:5176
echo API文档: http://localhost:8000/api/v1/docs
echo 默认账号: admin / admin123
echo ========================================
echo.
echo 请在浏览器中打开: http://localhost:5176
echo.
pause
