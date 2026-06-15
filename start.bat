@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo    AI Workbench 正在启动...
echo ========================================
echo.

:: 检查依赖是否已安装
if not exist "backend\requirements.txt" (
    echo ❌ 错误：找不到项目文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ⚠️  检测到前端依赖未安装
    echo 正在运行安装程序...
    echo.
    call install.bat
    if errorlevel 1 (
        echo.
        echo ❌ 依赖安装失败，请手动运行 install.bat
        pause
        exit /b 1
    )
)

:: 启动后端
echo [1/3] 启动后端服务 (端口 8000)...
start "AI Workbench - 后端" /MIN cmd /c "python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
echo ✅ 后端服务已启动

:: 启动前端
echo [2/3] 启动前端服务 (端口 5173)...
start "AI Workbench - 前端" /MIN cmd /c "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo ✅ 前端服务已启动

:: 等待服务就绪
echo [3/3] 等待服务就绪...
timeout /t 5 /nobreak >nul

:: 打开浏览器
echo.
echo ========================================
echo    ✅ 启动完成！
echo ========================================
echo.
echo 工作台地址: http://127.0.0.1:5173
echo 后端 API:   http://127.0.0.1:8000
echo.
echo 正在打开浏览器...
start http://127.0.0.1:5173
echo.
echo 提示：
echo - 两个黑色窗口会在后台运行（已最小化）
echo - 关闭它们会停止服务
echo - 再次运行此脚本会启动新实例
echo.
echo 按任意键关闭此窗口（服务继续运行）...
pause >nul
