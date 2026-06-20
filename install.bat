@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist "backend\requirements.txt" (
    echo Error: please run install.bat from the AI Workbench project folder.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    AI Workbench 安装向导
echo ========================================
echo.

:: 检测 Python
echo [1/5] 检测 Python...
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
echo [2/5] 检测 Node.js...
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

:: 检测可选 Codex CLI
echo.
echo [3/5] 检测可选 Codex CLI...
codex --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  未检测到 Codex CLI。普通 API 模式不需要它，启动后在「设置」里保存 API 配置即可使用。
) else (
    for /f "tokens=*" %%i in ('codex --version 2^>^&1') do set CODEX_VERSION=%%i
    echo ✅ 可选 Codex 环境：!CODEX_VERSION!
)

:: 安装后端依赖
echo.
echo [4/5] 安装后端依赖...
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
echo [5/5] 安装前端依赖...
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
echo 启动后如果没有 Codex CLI，请先进入「设置」保存 API Base URL、模型和 API Key
echo 后续使用可以直接双击 start.bat
echo.
pause
