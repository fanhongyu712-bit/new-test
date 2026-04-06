@echo off
chcp 65001 >nul
title 养老机构健康监测系统 - 前端服务
echo ========================================
echo   养老机构健康监测与风险预警系统
echo   前端服务启动脚本
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/3] 检查Node.js环境...
node --version
echo.

echo [2/3] 安装依赖（首次运行需要几分钟）...
if not exist "node_modules" (
    npm install
) else (
    echo 依赖已安装
)
echo [√] 依赖安装完成

echo [3/3] 启动前端服务...
echo.
echo ========================================
echo 正在启动前端服务...
echo.
echo 前端界面: http://localhost:5176
echo ========================================
echo.
npm run dev
