$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
if (-not $root) {
  $root = Split-Path -Parent $MyInvocation.MyCommand.Path
}

function Test-LocalUrl($url) {
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
    return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
  } catch {
    return $false
  }
}

function Start-WorkbenchProcess($title, $workingDirectory, $command) {
  Start-Process powershell -WindowStyle Hidden -ArgumentList @(
    "-NoExit",
    "-Command",
    "& { `$Host.UI.RawUI.WindowTitle = '$title'; Set-Location -LiteralPath '$workingDirectory'; $command }"
  )
}

if (-not (Test-Path -LiteralPath (Join-Path $root "backend\requirements.txt"))) {
  Write-Host "Startup failed: please run this script from the AI Workbench project folder."
  exit 1
}

if (-not (Test-Path -LiteralPath (Join-Path $root "frontend\node_modules"))) {
  Write-Host "Frontend dependencies are missing. Run install.bat first."
  exit 1
}

$apiUrl = "http://127.0.0.1:8000/api/health"
$webUrl = "http://127.0.0.1:5173"

Write-Host "Starting AI Workbench API on http://127.0.0.1:8000"
if (-not (Test-LocalUrl $apiUrl)) {
  Start-WorkbenchProcess "AI Workbench API" $root "python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
}

Write-Host "Starting AI Workbench UI on http://127.0.0.1:5173"
if (-not (Test-LocalUrl $webUrl)) {
  Start-WorkbenchProcess "AI Workbench UI" (Join-Path $root "frontend") "& npm.cmd run dev"
}

for ($i = 0; $i -lt 45; $i++) {
  if ((Test-LocalUrl $apiUrl) -and (Test-LocalUrl $webUrl)) {
    Write-Host "Opening browser on http://127.0.0.1:5173"
    Start-Process $webUrl
    exit 0
  }
  Start-Sleep -Seconds 1
}

Write-Host "AI Workbench did not become ready."
Write-Host "Check whether port 8000 or 5173 is already occupied, then keep this start.bat window open and try again."
exit 1
