@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo    AI Workbench 安装向导
echo ========================================
echo.

:: 检测 Python
echo [1/4] 检测 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python
    echo.
    echo 请先安装 Python 3.10 或更高版本：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION%

:: 检测 Node.js
echo [2/4] 检测 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Node.js
    echo.
    echo 请先安装 Node.js 20 或更高版本：
    echo https://nodejs.org/
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION%

:: 安装后端依赖
echo.
echo [3/4] 安装后端依赖...
python -m pip install --upgrade pip --quiet
python -m pip install -r backend\requirements.txt --quiet
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)
echo ✅ 后端依赖安装完成

:: 安装前端依赖
echo.
echo [4/4] 安装前端依赖...
cd frontend
call npm install --silent
if errorlevel 1 (
    cd ..
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
cd ..
echo ✅ 前端依赖安装完成

:: 完成
echo.
echo ========================================
echo    ✅ 安装完成！
echo ========================================
echo.
echo 下一步：运行 start.bat 启动工作台
echo 或者直接双击 start.bat
echo.
pause
