@echo off
chcp 65001 >nul
title 养老机构健康监测系统 - 后端服务（无虚拟环境）
echo ========================================
echo   养老机构健康监测与风险预警系统
echo   后端服务启动脚本（直接运行）
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] 安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
if %errorlevel% neq 0 (
    pip install -r requirements.txt -q
)
echo [√] 依赖安装完成

echo [2/3] 初始化数据库...
python -c "from app.init_data import main; import asyncio; asyncio.run(main())"
echo [√] 数据库初始化完成

echo [3/3] 启动后端服务...
echo.
echo ========================================
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/api/v1/docs
echo 默认账号: admin / admin123
echo ========================================
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
