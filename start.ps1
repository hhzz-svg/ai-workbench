$ErrorActionPreference = "Stop"

Write-Host "Starting Skill Workbench API on http://127.0.0.1:8000"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$PSScriptRoot'; python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
)

Write-Host "Starting Skill Workbench UI on http://127.0.0.1:5173"
npm --prefix "$PSScriptRoot\frontend" install
npm --prefix "$PSScriptRoot\frontend" run dev
