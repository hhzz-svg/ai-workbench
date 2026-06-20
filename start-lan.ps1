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

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -ne "127.0.0.1" } |
  Select-Object -First 1 -ExpandProperty IPAddress)

$apiUrl = "http://127.0.0.1:8000/api/health"
$webUrl = "http://127.0.0.1:5173"

Write-Host "Starting API on http://127.0.0.1:8000"
if (-not (Test-LocalUrl $apiUrl)) {
  Start-WorkbenchProcess "AI Workbench API" $root "python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
}

Write-Host "Starting LAN UI on http://0.0.0.0:5173"
if (-not (Test-LocalUrl $webUrl)) {
  Start-WorkbenchProcess "AI Workbench LAN UI" (Join-Path $root "frontend") "& npm.cmd run dev -- --host 0.0.0.0"
}

for ($i = 0; $i -lt 45; $i++) {
  if ((Test-LocalUrl $apiUrl) -and (Test-LocalUrl $webUrl)) {
    if ($ip) {
      Write-Host "Other devices on the same network can open: http://$ip:5173"
    } else {
      Write-Host "LAN address was not detected. Open this computer at http://127.0.0.1:5173"
    }
    exit 0
  }
  Start-Sleep -Seconds 1
}

Write-Host "AI Workbench LAN mode did not become ready."
Write-Host "Check whether port 8000 or 5173 is already occupied, then try again."
exit 1
