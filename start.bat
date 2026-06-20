@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist "backend\requirements.txt" (
  echo Error: please run this script from the AI Workbench project folder.
  pause
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo Frontend dependencies are missing. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo Install failed. Please check the install window output.
    pause
    exit /b 1
  )
)

python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo Backend dependencies are missing. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo Install failed. Please check the install window output.
    pause
    exit /b 1
  )
)

echo Starting AI Workbench...
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%start.ps1"

if errorlevel 1 (
  echo.
  echo Startup failed. Please check the error above.
  pause
  exit /b 1
)

pause
