$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
if (-not $root) {
  $root = Split-Path -Parent $MyInvocation.MyCommand.Path
}

function Test-LocalUrl($url) {
  try {
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
    return $resp.StatusCode -eq 200
  } catch {
    return $false
  }
}

Write-Host "Starting Skill Workbench API on http://127.0.0.1:8000"
if (-not (Test-LocalUrl "http://127.0.0.1:8000/api/health")) {
  Start-Process powershell -WindowStyle Hidden -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location -LiteralPath '$root'; python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
  )
}

Write-Host "Starting Skill Workbench UI on http://127.0.0.1:5173"
if (-not (Test-LocalUrl "http://127.0.0.1:5173")) {
  Start-Process powershell -WindowStyle Hidden -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location -LiteralPath '$root\frontend'; & npm.cmd run dev"
  )
}

for ($i = 0; $i -lt 30; $i++) {
  if ((Test-LocalUrl "http://127.0.0.1:8000/api/health") -and (Test-LocalUrl "http://127.0.0.1:5173")) {
    Write-Host "Opening browser on http://127.0.0.1:5173"
    Start-Process "http://127.0.0.1:5173"
    exit 0
  }
  Start-Sleep -Seconds 1
}

Write-Host "AI Workbench did not become ready. Check whether ports 8000 and 5173 are already occupied."
exit 1
